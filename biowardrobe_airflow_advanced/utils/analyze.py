#!/usr/bin/env python3
import os
import logging
import argparse
import decimal
from json import dumps, loads
from collections import OrderedDict
from biowardrobe_airflow_advanced.utils.connect import HookConnect


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


def get_settings_data():
    logger.debug(f"Collecting data from settings")
    connect_db = HookConnect()
    settings = connect_db.get_settings()
    settings_data = {
        "raw_data": norm_path("/".join((settings['wardrobe'], settings['preliminary']))),
        "anl_data": norm_path("/".join((settings['wardrobe'], settings['advanced']))),
        "upload":   norm_path("/".join((settings['wardrobe'], settings['upload']))),
        "indices":  norm_path("/".join((settings['wardrobe'], settings['indices']))),
        "threads": settings['maxthreads'],
        "experimentsdb": settings['experimentsdb']
    }
    return settings_data


def get_files(current_dir, filename_pattern=".*"):
    """Files with the identical basenames are overwritten"""
    files_dict = {}
    for root, dirs, files in os.walk(current_dir):
        files_dict.update(
            {filename: os.path.join(root, filename) for filename in files if re.match(filename_pattern, filename)}
        )
    return files_dict


def norm_path(path):
    return os.path.abspath(os.path.normpath(os.path.normcase(path)))


def get_workflow(workflow_name):
    workflows_folder = norm_path(os.path.join(os.path.dirname(os.path.abspath(os.path.join(__file__, "../"))), "cwls"))
    return get_files(workflows_folder)[workflow_name]


def complete_input(item):
    monitor = {"found_none": False}
    recursive_check(item, monitor)
    return not monitor["found_none"]


def recursive_check(item, monitor):
    if item == 'None' or (isinstance(item, str) and 'None' in item):
        monitor["found_none"] = True
    elif isinstance(item, dict):
        dict((k, v) for k, v in item.items() if recursive_check(v, monitor))
    elif isinstance(item, list):
        list(v for v in item if recursive_check(v, monitor))


def remove_not_set_inputs(job_object):
    job_object_filtered ={}
    for key, value in job_object.items():
        if complete_input(value):
            job_object_filtered[key] = value
    return job_object_filtered


def fill_template(template, kwargs):
    job_object = remove_not_set_inputs(loads(template.replace('\n', ' ').format(**kwargs).
                                             replace("'True'", 'true').replace("'False'", 'false').
                                             replace('"True"', 'true').replace('"False"', 'false')))
    return OrderedDict(sorted(job_object.items()))


def normalize_args(args, skip_list=[]):
    """Converts all relative path arguments to absolute ones relatively to the current working directory"""
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)


def get_deseq_job(conf):
    logger.debug(f"Collecting data for genelists:\n"
                 f"  untreated -  {conf['condition'][0]}\n"
                 f"  treated -    {conf['condition'][1]}\n"
                 f"  groupby -    {conf['groupby']}\n"
                 f"  result_uid - {conf['result_uid']}")
    setting_data = get_settings_data()
    job = {
        "untreated_files": [],
        "treated_files": [],
        "output_filename": conf['result_uid'] + "_deseq.tsv",
        "threads": int(setting_data["threads"]),
        "output_folder": os.path.join(setting_data["anl_data"], conf['result_uid']),
        "uid": conf['result_uid']}
    connect_db = HookConnect()
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

