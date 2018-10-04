#! /usr/bin/env python3
import sys
import logging
import argparse

from biowardrobe_airflow_advanced.utils.connect import HookConnect, DirectConnect
from biowardrobe_airflow_advanced.utils.utilities import normalize_args
from biowardrobe_airflow_advanced.utils.initialize import (gen_outputs,
                                                           create_pools,
                                                           create_dags)


logger = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced', add_help=True)
    parser.add_argument("-c", "--config", help="Path to the BioWardrobe config file", default="/etc/wardrobe/wardrobe")
    return parser


def setup_airflow(config):
    HookConnect(config)  # Need to run it with config at least once to create connection
    create_pools("biowardrobe_advanced", 10, "Pool to run BioWardrobe Advanced Analysis")
    create_dags()


def setup_biowardrobe(config):
    db_connection_handler = DirectConnect(config)
    gen_outputs(db_connection_handler)


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args)
    setup_biowardrobe(args.config)
    setup_airflow(args.config)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


