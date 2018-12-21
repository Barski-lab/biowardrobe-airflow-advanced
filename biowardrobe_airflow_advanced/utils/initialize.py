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
                                                          norm_path,
                                                          get_files)


logger = logging.getLogger(__name__)
SCRIPTS_DIR = norm_path(os.path.join(os.path.dirname(os.path.abspath(os.path.join(__file__, "../"))), "scripts"))
SQL_DIR = norm_path(os.path.join(os.path.dirname(os.path.abspath(os.path.join(__file__, "../"))), "sql_patches"))


def create_dags():
    deseq_template = u"""#!/usr/bin/env python3
from airflow import DAG
from biowardrobe_airflow_advanced import biowardrobe_advanced
from biowardrobe_airflow_advanced.operators import DeseqJobDispatcher, DeseqJobGatherer
dag = biowardrobe_advanced("deseq-advanced.cwl", DeseqJobDispatcher, DeseqJobGatherer, "biowardrobe_advanced")"""
    export_to_file(deseq_template, os.path.join(DAGS_FOLDER, "deseq-advanced.py"))

    heatmap_template = u"""#!/usr/bin/env python3
from airflow import DAG
from biowardrobe_airflow_advanced import biowardrobe_advanced
from biowardrobe_airflow_advanced.operators import HeatmapJobDispatcher, HeatmapJobGatherer
dag = biowardrobe_advanced("heatmap.cwl", HeatmapJobDispatcher, HeatmapJobGatherer, "biowardrobe_advanced")"""
    export_to_file(heatmap_template, os.path.join(DAGS_FOLDER, "heatmap.py"))

    pca_template = u"""#!/usr/bin/env python3
from airflow import DAG
from biowardrobe_airflow_advanced import biowardrobe_advanced
from biowardrobe_airflow_advanced.operators import PcaJobDispatcher, PcaJobGatherer
dag = biowardrobe_advanced("pca.cwl", PcaJobDispatcher, PcaJobGatherer, "biowardrobe_advanced")"""
    export_to_file(pca_template, os.path.join(DAGS_FOLDER, "pca.py"))


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


def apply_patches(connect_db):
    logger.debug(f"Applying SQL patches from {SQL_DIR}")
    bw_patches = get_files(os.path.join(SQL_DIR, "biowardrobe"), ".*sql$")
    for filename in bw_patches.values():
        try:
            connect_db.apply_patch(filename)
        except Exception as ex:
            logger.debug(f"Failed to apply patch {filename} due to\n {ex}")


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
    logger.debug(f"Run SQL query:\n{sql_query}")
    for db_record in connect_db.fetchall(sql_query):
        logger.info(f"LOAD: {db_record['uid']} - {db_record['exp_type']}")
        get_to_update_stage = False
        get_to_upload_stage = False
        db_record.update(setting_data)
        db_record.update({"prefix": SCRIPTS_DIR})
        db_record.update({"outputs": loads(db_record["outputs"]) if db_record["outputs"] and db_record['outputs'] != "null" else {}})

        for item_str in TEMPLATES.get(db_record["exp_id"], []):
            try:
                logger.debug(f"CHECK: if experiment's outputs require correction")
                item_parsed = fill_template(item_str, db_record)
                list(validate_locations(item_parsed["outputs"]))  # TODO Use normal way to execute generator
                validate_outputs(db_record["outputs"], item_parsed["outputs"])
            except KeyError as ex:
                logger.info(f"SKIP: couldn't find required experiment's output {ex}")
            except OSError as ex:
                get_to_update_stage = True
                logger.debug(f"GENERATE: missing file or correpospondent data in DB: {ex}")
                try:
                    commands = " ".join(item_parsed["commands"])
                    logger.debug(f"RUN: {commands}")
                    run_command(commands)
                    add_details_to_outputs(item_parsed["outputs"])
                    db_record["outputs"].update(item_parsed["outputs"])
                    get_to_upload_stage = True
                except subprocess.CalledProcessError as ex:
                    logger.error(f"FAIL: got error while running the command {ex}")
                except OSError as ex:
                    logger.error(f"FAIL: couldn't locate generated files {ex}")

        if get_to_upload_stage:
            connect_db.execute(f"""UPDATE labdata SET params='{dumps(db_record["outputs"])}' WHERE uid='{db_record["uid"]}'""")
            logger.debug(f"UPDATE: new experiment's outputs\n{dumps(db_record['outputs'], indent=4)}")
            logger.info(f"SUCCESS: experiment's outputs have been corrected")
        elif get_to_update_stage:
            logger.info(f"FAIL: experiment's outputs have not been corrected")
        else:
            logger.info(f"SUCCESS: experiment's outputs are not required or cannot be corrected")






