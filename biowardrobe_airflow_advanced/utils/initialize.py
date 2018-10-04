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
                                                          export_to_file)


logger = logging.getLogger(__name__)


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
        try:
            exp_outputs = loads(db_record["outputs"]) if db_record["outputs"] and db_record['outputs'] != "null" else {}
            db_record.update(setting_data)
            for item in TEMPLATES[db_record["exp_id"]]:
                item["outputs"] = fill_template(item["outputs"], db_record)
                item["script"] = item["script"].format(**db_record)
                try:
                    validate_locations(item["outputs"])
                except OSError:
                    logger.debug(f"Missing required outputs for {exp_outputs['uid']}")
                    try:
                        run_command(item["script"])
                        add_details_to_outputs(item["outputs"])
                        exp_outputs.update(item["outputs"])
                    except subprocess.CalledProcessError as ex:
                        logger.error(f"""Failed to generate outputs for {exp_outputs["uid"]}\n{str(ex)}""")
            connect_db.execute(f"""UPDATE labdata SET params='{dumps(exp_outputs)}' WHERE uid='{db_record["uid"]}'""")
            logger.info(f"""Update params for {db_record['uid']}\n {dumps(exp_outputs, indent=4)}""")
        except Exception as ex:
            logger.error(f"Failed to updated params for {db_record['uid']}\n {str(ex)}")


