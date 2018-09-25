#!/usr/bin/env python3
import logging
import decimal
import os
import re
from json import dumps, loads
from biowardrobe_airflow_plugins.utils.connect import HookConnect
from biowardrobe_airflow_plugins.utils.func import (norm_path, fill_template)
from biowardrobe_airflow_plugins.utils.upload import process_results


logger = logging.getLogger(__name__)


def get_exp_data(uid):
    logger.debug(f"Collecting data for: {uid}")
    connect_db = HookConnect()
    sql_query = f"""SELECT 
                        l.params as outputs,
                        e.id     as exp_type_id,
                        g.findex as genome_type,
                    FROM labdata l
                    INNER JOIN (experimenttype e, genome g) ON (e.id=l.experimenttype_id AND g.id=l.genome_id)
                    LEFT JOIN (antibody a) ON (l.antibody_id=a.id)
                    WHERE l.uid='{uid}'"""
    logger.debug(f"Running SQL query:\n{sql_query}")
    kwargs = connect_db.fetchone(sql_query)
    logger.debug(f"Collecting SQL query results:\n{kwargs}")
    kwargs = {key: (value if not isinstance(value, decimal.Decimal) else int(value)) for key, value in kwargs.items()}
    kwargs.update({"outputs": loads(kwargs['outputs']) if kwargs['outputs'] else {}})
    logger.debug(f"Collected data for: {uid}\n{dumps(kwargs, indent=4)}")
    return kwargs


def get_settings_data():
    logger.debug(f"Collecting data from settings")
    connect_db = HookConnect()
    settings = connect_db.get_settings()
    kwargs = {
        "raw_data": norm_path("/".join((settings['wardrobe'], settings['preliminary']))),
        "anl_data": norm_path("/".join((settings['wardrobe'], settings['advanced']))),
        "upload":   norm_path("/".join((settings['wardrobe'], settings['upload']))),
        "indices":  norm_path("/".join((settings['wardrobe'], settings['indices']))),
        "threads": settings['maxthreads'],
        "experimentsdb": settings['experimentsdb']
    }
    return kwargs


def get_advanced_data(conf, workflow):
    # WARNING: will fail if not DESeq workflow. Should be updated, once new workflows added

    logger.debug(f"Collecting data for genelists:\n"
                 f"  untreated -  {conf['condition'][0]}\n"
                 f"  treated -    {conf['condition'][1]}\n"
                 f"  groupby -    {conf['grouping']}\n"
                 f"  result_uid - {conf['result_uid']}")
    connect_db = HookConnect()

    job_data = {"untreated_files": [],
                "treated_files": [],
                "uid": conf['result_uid']}
    for idx, uid in enumerate(conf['condition']):
        sql_query = f"SELECT tableName as exp_uid FROM genelist WHERE leaf=1 AND (parent_id like '{uid}' OR id like '{uid}')"
        class_template = '{{"class": "File", "location": "{outputs[rpkm_isoforms][location]}", "format": "{outputs[rpkm_isoforms][format]}"}'
        for exp_uid in connect_db.fetchall(sql_query):
            exp_data = get_exp_data(exp_uid)
            if idx == 0:
                job_data["untreated_files"].append(fill_template(class_template, exp_data))
            else:
                job_data["treated_files"].append(fill_template(class_template, exp_data))
    job_data.update(get_settings_data())

    job_data.update({"advanced": {adv_exp['workflow']: {'id':           adv_exp['id'],
                                                        'atype':        adv_exp['atype'],
                                                        'etype_id':     adv_exp['etype_id'],
                                                        'pool':         adv_exp['pool'],
                                                        'job':          fill_template(adv_exp['template'], job_data),
                                                        'upload_rules': fill_template(adv_exp['upload_rules'], job_data)}
                                  for adv_exp in connect_db.fetchall(f"SELECT * FROM advancedtype WHERE workflow='{workflow}'")}})
    return job_data

