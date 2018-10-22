#! /usr/bin/env python3
import os
import sys
import argparse
from json import dumps, load


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced Load Heatmap', add_help=True)
    parser.add_argument("-f", "--folder", help="Path to the folder with heatmap files to be refactored", required=True)
    return parser


def get_collected_heatmap_data(folder):
    data = []
    for heatmap_file in os.listdir(folder):
        with open(os.path.join(folder, heatmap_file), 'r') as input_stream:
            heatmap_data = load(input_stream)
        data.append({
            "array":     heatmap_data["data"],
            "rows":      heatmap_data["index"],
            "cols":      heatmap_data["columns"],
            "pltname":   None,
            "tbl1_id":   None,
            "tbl2_id":   None,
            "bodyarray": [],
            "genebody":  [],
            "rpkmarray": [],
            "rpkmcols":  [],
            "glengths": [],
            "mapped":    None,
            "max":       None,
            "tbl1_name": None,
            "tbl2_name": None
        })
    collected_heatmap_data = {
        "data": data,
        "message": "Data populated",
        "total": len(data),
        "success": True
    }
    return collected_heatmap_data


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args.folder = args.folder if os.path.isabs(args.folder) else os.path.normpath(os.path.join(os.getcwd(), args.folder))
    print(dumps(get_collected_heatmap_data(args.folder)))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))