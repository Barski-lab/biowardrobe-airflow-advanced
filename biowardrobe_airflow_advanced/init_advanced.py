#! /usr/bin/env python3
import os
import sys
import logging
import argparse
from biowardrobe_airflow_plugins.utils.connect import (DirectConnect, HookConnect)
from biowardrobe_airflow_plugins.utils.func import (norm_path,
                                                    normalize_args,
                                                    get_files)
from airflow.settings import DAGS_FOLDER
from airflow.bin.cli import api_client


logger = logging.getLogger(__name__)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced', add_help=True)
    parser.add_argument("-c", "--config", help="Path to the BioWardrobe config file", default="/etc/wardrobe/wardrobe")
    return parser


def apply_patches(connect_db):
    bw_patches = get_files(norm_path(os.path.join(CURRENT_DIR, "sql_patches", "biowardrobe")), ".*sql$")
    if not connect_db.fetchone("SHOW TABLES LIKE 'advancedtype'"):
        connect_db.apply_patch(bw_patches["advanced_type_create.sql"])
    connect_db.apply_patch(bw_patches["advanced_type_patch.sql"])


def export_dag(template, filename, params={}):
    with open(filename, 'w') as output_stream:
        output_stream.write(template.format(**params))


def create_pools(pool, slots=10, description=""):
    try:
        pools = [api_client.get_pool(name=pool)]
    except Exception:
        api_client.create_pool(name=pool, slots=slots, description=description)


def create_dags():
    connect_db = HookConnect()
    advanced_template = u"""
        #!/usr/bin/env python3
        from airflow import DAG
        from biowardrobe_airflow_advanced import biowardrobe_advanced
        from biowardrobe_airflow_advanced.operators import {job_dispatcher}
        from biowardrobe_airflow_advanced.operators import {job_gatherer}
        dag = biowardrobe_advanced("{workflow}", {job_dispatcher}, {job_gatherer}, "{pool}")"""
    for wf_filename, path in get_files(os.path.join(CURRENT_DIR, "cwls")).items():
        advancedtype_data = connect_db.fetchone(f"SELECT * FROM advancedtype WHERE workflow='{wf_filename}'")
        create_pools(advancedtype_data["pool"], 10, "Pool to run BioWardrobe Advanced Analysis")
        export_dag(template=advanced_template,
                   filename=os.path.join(DAGS_FOLDER, os.path.splitext(wf_filename)[0] + ".py"),
                   params=advancedtype_data)


def create_connection(config):
    HookConnect(config)


def setup_airflow(config):
    create_connection(config)
    create_dags()


def setup_biowardrobe(config):
    db_connection_handler = DirectConnect(config)
    apply_patches(db_connection_handler)


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args)

    setup_biowardrobe(args.config)
    setup_airflow(args.config)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


