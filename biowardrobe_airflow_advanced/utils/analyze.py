#!/usr/bin/env python3
import os
import logging
import decimal
from json import dumps, loads

from biowardrobe_airflow_advanced.utils.connect import HookConnect
from biowardrobe_airflow_advanced.utils.utilities import norm_path, get_files, fill_template


logger = logging.getLogger(__name__)


def get_exp_data(uid):
    logger.debug(f"Collecting data for: {uid}")
    connect_db = HookConnect()
    sql_query = f"""SELECT 
                        l.params as outputs,
                        e.id     as exp_type_id,
                        g.findex as genome_type
                    FROM labdata l
                    INNER JOIN (experimenttype e, genome g) ON (e.id=l.experimenttype_id AND g.id=l.genome_id)
                    LEFT JOIN (antibody a) ON (l.antibody_id=a.id)
                    WHERE l.uid='{uid}'"""
    logger.debug(f"Running SQL query:\n{sql_query}")
    exp_data = connect_db.fetchone(sql_query)
    exp_data = {key: (value if not isinstance(value, decimal.Decimal) else int(value)) for key, value in exp_data.items()}
    exp_data.update({"outputs": loads(exp_data['outputs']) if exp_data['outputs'] else {}})
    logger.debug(f"Collected data for: {uid}\n{dumps(exp_data, indent=4)}")
    return exp_data


def get_workflow(workflow_name):
    workflows_folder = norm_path(os.path.join(os.path.dirname(os.path.abspath(os.path.join(__file__, "../"))), "cwls"))
    return get_files(workflows_folder)[workflow_name]


def get_deseq_job(conf):
    logger.debug(f"Collecting data for genelists:\n"
                 f"  untreated -  {conf['condition'][0]}\n"
                 f"  treated -    {conf['condition'][1]}\n"
                 f"  groupby -    {conf['groupby']}\n"
                 f"  result_uid - {conf['result_uid']}")
    connect_db = HookConnect()
    setting_data = connect_db.get_settings_data()
    job = {
        "untreated_files": [],
        "treated_files": [],
        "output_filename": conf['result_uid'] + "_deseq.tsv",
        "threads": int(setting_data["threads"]),
        "output_folder": os.path.join(setting_data["anl_data"], conf['result_uid']),
        "uid": conf['result_uid']}

    for idx, uid in enumerate(conf['condition']):
        logger.debug(f"Get experiment ids for {uid}")
        sql_query = f"SELECT tableName FROM genelist WHERE leaf=1 AND (parent_id like '{uid}' OR id like '{uid}')"
        file_template = '{{"class": "File", "location": "{outputs[rpkm_isoforms][location]}", "format": "http://edamontology.org/format_3752"}}'
        for record in connect_db.fetchall(sql_query):
            exp_data = get_exp_data(record["tableName"])
            if idx == 0:
                job["untreated_files"].append(fill_template(file_template, exp_data))
            else:
                job["treated_files"].append(fill_template(file_template, exp_data))
    return job
