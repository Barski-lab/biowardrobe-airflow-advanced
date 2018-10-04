import os
import logging
import subprocess
from json import dumps, loads

from airflow.settings import DAGS_FOLDER
from airflow.bin.cli import api_client

from biowardrobe_airflow_advanced.templates.outputs import TEMPLATES
from biowardrobe_airflow_advanced.utils.utilities import (validate_locations,
                                                          add_details_to_outputs,
                                                          fill_template,
                                                          run_command,
                                                          export_to_file,
                                                          norm_path)


logger = logging.getLogger(__name__)
SCRIPTS_DIR = norm_path(os.path.join(os.path.dirname(os.path.abspath(os.path.join(__file__, "../"))), "scripts"))


def create_dags():
    deseq_template = u"""#!/usr/bin/env python3
from airflow import DAG
from biowardrobe_airflow_advanced import biowardrobe_advanced
from biowardrobe_airflow_advanced.operators import DeseqJobDispatcher, DeseqJobGatherer
dag = biowardrobe_advanced("deseq-advanced.cwl", DeseqJobDispatcher, DeseqJobGatherer, "biowardrobe_advanced")"""
    export_to_file(deseq_template, os.path.join(DAGS_FOLDER, "deseq-advanced.py"))


def create_pools(pool, slots=10, description=""):
    try:
        pools = [api_client.get_pool(name=pool)]
    except Exception:
        api_client.create_pool(name=pool, slots=slots, description=description)


def validate_outputs(superset, subset):
    try:
        dummy = [superset[key] for key, val in subset.items()]
    except KeyError:
        raise OSError


def gen_outputs(connect_db):
    setting_data = connect_db.get_settings_data()
    sql_query = """SELECT
                         l.uid                    as uid,
                         l.params                 as outputs,
                         e.etype                  as exp_type,
                         e.id                     as exp_id
                   FROM  labdata l
                   INNER JOIN (experimenttype e) ON (e.id=l.experimenttype_id)
                   WHERE (l.deleted=0)                 AND
                         (l.libstatus=12)              AND
                         COALESCE(l.egroup_id,'')<>''  AND
                         COALESCE(l.name4browser,'')<>''"""
    for db_record in connect_db.fetchall(sql_query):
        upload = False
        db_record.update(setting_data)
        db_record.update({"prefix": SCRIPTS_DIR})
        db_record.update({"outputs": loads(db_record["outputs"]) if db_record["outputs"] and db_record['outputs'] != "null" else {}})
        for item_str in TEMPLATES.get(db_record["exp_id"], []):
            try:
                item_parsed = fill_template(item_str, db_record)
                list(validate_locations(item_parsed["outputs"]))  # TODO Use normal way to execute generator
                validate_outputs(db_record["outputs"], item_parsed["outputs"])
            except KeyError as ex:
                print("Skip generating output for ", db_record["uid"],  ex)
            except OSError as ex:
                print("Missing required output", ex)
                try:
                    run_command(" ".join(item_parsed["commands"]))
                    add_details_to_outputs(item_parsed["outputs"])
                    db_record["outputs"].update(item_parsed["outputs"])
                    upload = True
                except subprocess.CalledProcessError as ex:
                    print("Failed to generate outputs: ", ex)
        if upload:
            connect_db.execute(f"""UPDATE labdata SET params='{dumps(db_record["outputs"])}' WHERE uid='{db_record["uid"]}'""")
            logger.info(f"""Update params for {db_record['uid']}\n {dumps(db_record["outputs"], indent=4)}""")



