#! /usr/bin/env python3
import os
import sys
import logging
import argparse
from biowardrobe_airflow_advanced.utils.connect import HookConnect
from biowardrobe_airflow_advanced.utils.analyze import normalize_args
from airflow.settings import DAGS_FOLDER
from airflow.bin.cli import api_client


logger = logging.getLogger(__name__)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced', add_help=True)
    parser.add_argument("-c", "--config", help="Path to the BioWardrobe config file", default="/etc/wardrobe/wardrobe")
    return parser


def export_dag(template, filename, params={}):
    with open(filename, 'w') as output_stream:
        output_stream.write(template.format(**params))


def create_pools(pool, slots=10, description=""):
    try:
        pools = [api_client.get_pool(name=pool)]
    except Exception:
        api_client.create_pool(name=pool, slots=slots, description=description)


def create_dags():
    deseq_template = u"""#!/usr/bin/env python3
from airflow import DAG
from biowardrobe_airflow_advanced import biowardrobe_advanced
from biowardrobe_airflow_advanced.operators import DeseqJobDispatcher
from biowardrobe_airflow_advanced.operators import DeseqJobGatherer
dag = biowardrobe_advanced("deseq-biowardrobe-only.cwl", DeseqJobDispatcher, DeseqJobGatherer, "biowardrobe_advanced")"""
    export_dag(template=deseq_template, filename=os.path.join(DAGS_FOLDER, "advanced-deseq.py"))


def setup_airflow(config):
    HookConnect(config)  # Need to run it with config to create connection
    create_pools("biowardrobe_advanced", 10, "Pool to run BioWardrobe Advanced Analysis")
    create_dags()


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args)
    setup_airflow(args.config)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


