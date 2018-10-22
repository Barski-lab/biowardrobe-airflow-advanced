#! /usr/bin/env python3
import sys
import logging
import argparse
from json import dumps

from biowardrobe_airflow_advanced.utils.mute import Mute
with Mute():  # Suppress output
    from biowardrobe_airflow_advanced.utils.analyze import get_collected_heatmap_data
    from biowardrobe_airflow_advanced.utils.logger import reset_root_logger


logger = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced Load Heatmap', add_help=True)
    parser.add_argument("-u", "--uid", help="Genelist UID", required=True)
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all output except warnings and errors")
    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)

    with Mute():
        reset_root_logger(args.quiet)

    print(dumps(get_collected_heatmap_data(args.uid)))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))