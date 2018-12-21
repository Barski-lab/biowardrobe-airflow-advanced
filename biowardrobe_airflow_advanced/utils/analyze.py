#!/usr/bin/env python3
import os
import logging
import decimal
from json import dumps, loads, load

from biowardrobe_airflow_advanced.utils.connect import HookConnect
from biowardrobe_airflow_advanced.utils.utilities import norm_path, get_files, fill_template, export_to_file



logger = logging.getLogger(__name__)


def get_heatmap_job(conf):
    logger.debug(f"Collecting data for genelist:\n"
                 f"  name          - {conf['name']}\n"
                 f"  uid           - {conf['uid']}\n"
                 f"  data_uid      - {conf['data_uid']}\n"
                 f"  intervals_uid - {conf['intervals_uid']}\n")
    connect_db = HookConnect()
    setting_data = connect_db.get_settings_data()
    exp_data = get_exp_data(get_genelist_data(conf['data_uid'])["tableName"])
    job = {
        "bam_file":      fill_template('{{"class": "File", "location": "{outputs[bambai_pair][location]}", "format": "http://edamontology.org/format_2572"}}', exp_data),
        "genelist_file": get_genelist_file(conf['intervals_uid']),
        "fragment_size": exp_data["fragment_size"],
        "json_filename": "-".join([conf['data_uid'], conf['intervals_uid']]),
        "plot_name": conf['name'],
        "data_uid": conf['data_uid'],
        "data_name": get_genelist_data(conf['data_uid'])["name"],
        "intervals_uid": conf['intervals_uid'],
        "intervals_name": get_genelist_data(conf['intervals_uid'])["name"],
        "threads": int(setting_data["threads"]),
        "output_folder": os.path.join(setting_data["anl_data"], conf["uid"]),
        "uid": conf["uid"]
    }
    return job


def get_pca_job(conf):
    logger.debug(f"Generate job for PCA:\n"
                 f"  uid -        {conf['uid']}\n"
                 f"  expression - {conf['expression'][0]}\n")
    connect_db = HookConnect()
    setting_data = connect_db.get_settings_data()
    job = {
        "expression_file": [],
        "legend_name": [],
        "output_prefix": conf["uid"] + "_",
        "output_folder": os.path.join(setting_data["anl_data"], conf["uid"]),
        "uid": conf["uid"]}
    for idx, uid in enumerate(conf['expression']):
        genelist_data = get_genelist_data(uid)
        exp_data = get_exp_data(genelist_data["tableName"])
        job["expression_file"].append(f"""{{"class": "File",
                                            "location": "{exp_data[rpkm_isoforms][location]}",
                                            "format": "http://edamontology.org/format_3752"}}""")
        job["legend_name"].append(genelist_data["name"])
    return job


def get_genelist_file(uid):
    genelist_data = get_genelist_data(uid)
    genelist_file_template = '{{"class": "File", "location": "{outputs[genelist_file][location]}", "format": "http://edamontology.org/format_3475"}}'
    try:
        genelist_file = fill_template(genelist_file_template, genelist_data)
    except KeyError:
        logger.debug(f"Failed to find genelist file for: {uid}")
        connect_db = HookConnect()
        filename = os.path.join(connect_db.get_settings_data()["anl_data"], uid, uid+"_genelist.tsv")

        data = connect_db.fetchall(f"""SELECT * FROM experiments.{genelist_data["tableName"]}""")
        data_str = ""
        for idx, record in enumerate(data):
            if idx == 0:
                data_str += "\t".join([str(item) for item in record.keys()]) + "\n"
            else:
                data_str += "\t".join([str(item) for item in record.values()]) + "\n"

        export_to_file(data_str, filename)
        logger.debug(f"Export genelist file to: {filename}")
        genelist_data["outputs"].update({"genelist_file": {
                                            "class": "File",
                                            "location": filename,
                                            "format": "http://edamontology.org/format_3475"}
                                         })
        connect_db.execute(f"""UPDATE genelist SET params='{dumps(genelist_data["outputs"])}' WHERE id='{uid}'""")
        logger.debug(f"""Update params for {uid}\n{dumps(genelist_data["outputs"], indent=4)}""")
        genelist_file = fill_template(genelist_file_template, genelist_data)
    return genelist_file


def get_exp_data(uid):
    logger.debug(f"Collecting data for: {uid}")
    connect_db = HookConnect()
    sql_query = f"""SELECT 
                        l.params as outputs,
                        e.id     as exp_type_id,
                        g.findex as genome_type,
                        l.fragmentsize as fragment_size
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
                 f"  name -           {conf['name']}\n"
                 f"  project_uid -    {conf['project_uid']}\n"
                 f"  uid -            {conf['uid']}\n"
                 f"  untreated -      {conf['condition'][0]}\n"
                 f"  treated -        {conf['condition'][1]}\n"
                 f"  groupby -        {conf['groupby']}\n")

    connect_db = HookConnect()
    setting_data = connect_db.get_settings_data()
    job = {
        "untreated_files": [],
        "treated_files": [],
        "output_filename": conf["uid"] + "_deseq.tsv",
        "threads": int(setting_data["threads"]),
        "output_folder": os.path.join(setting_data["anl_data"], conf["uid"]),
        "uid": conf["uid"]}

    for idx, uid in enumerate(conf['condition']):
        logger.debug(f"Get experiment IDs for {uid}")
        sql_query = f"SELECT tableName FROM genelist WHERE leaf=1 AND (parent_id like '{uid}' OR id like '{uid}')"
        file_templates = {
            1: '{{"class": "File", "location": "{outputs[rpkm_isoforms][location]}", "format": "http://edamontology.org/format_3752"}}',
            2: '{{"class": "File", "location": "{outputs[rpkm_genes][location]}", "format": "http://edamontology.org/format_3475"}}',
            3: '{{"class": "File", "location": "{outputs[rpkm_common_tss][location]}", "format": "http://edamontology.org/format_3475"}}'
        }
        current_file_template = file_templates[conf["groupby"]]
        for record in connect_db.fetchall(sql_query):
            exp_data = get_exp_data(record["tableName"])
            if idx == 0:
                job["untreated_files"].append(fill_template(current_file_template, exp_data))
            else:
                job["treated_files"].append(fill_template(current_file_template, exp_data))
    return job


def get_genelist_data(uid):
    logger.debug(f"Collecting data from genelist for: {uid}")
    connect_db = HookConnect()
    sql_query = f"""SELECT name,
                           leaf,
                           type,
                           conditions,
                           gblink,
                           db,
                           tableName,
                           labdata_id,
                           rtype_id,
                           atype_id,
                           project_id,
                           parent_id,
                           params as outputs
                    FROM genelist
                    WHERE id LIKE '{uid}'"""
    logger.debug(f"Running SQL query:\n{sql_query}")
    glist_data = connect_db.fetchone(sql_query)
    glist_data = {key: (value if not isinstance(value, decimal.Decimal) else int(value)) for key, value in glist_data.items()}
    glist_data.update({"outputs": loads(glist_data['outputs']) if glist_data['outputs'] else {}})
    logger.debug(f"Collected data from genelist for: {uid}\n{dumps(glist_data, indent=4)}")
    return glist_data


def get_atdp_data(uid):
    logger.debug(f"Collecting data from atdp for: {uid}")
    connect_db = HookConnect()
    sql_query = f"""SELECT
                        tbl1_id as data_uid,
                        tbl2_id as intervals_uid,
                        pltname as name,
                        params as outputs
                    FROM atdp
                    WHERE genelist_id='{uid}'"""
    logger.debug(f"Running SQL query:\n{sql_query}")
    atdp_data = []
    for data in connect_db.fetchall(sql_query):
        data.update({"outputs": loads(data['outputs']) if data['outputs'] else {}})
        atdp_data.append(data)
    logger.debug(f"Collected data from atdp for: {uid}\n{dumps(atdp_data, indent=4)}")
    return atdp_data
