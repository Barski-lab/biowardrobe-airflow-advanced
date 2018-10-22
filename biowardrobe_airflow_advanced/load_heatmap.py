#! /usr/bin/env python3
import sys
import logging
import argparse

from biowardrobe_airflow_advanced.utils.analyze import get_collected_heatmap_data


logger = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced Load Heatmap', add_help=True)
    parser.add_argument("-u", "--uid", help="Genelist UID", required=True)
    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    print(get_collected_heatmap_data(args.uid))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))