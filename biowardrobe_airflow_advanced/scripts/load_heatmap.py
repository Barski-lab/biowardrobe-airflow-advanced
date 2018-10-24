#! /usr/bin/env python3
import os
import sys
import argparse
import random
from json import dumps, load


def get_parser():
    parser = argparse.ArgumentParser(description='BioWardrobe Airflow Advanced Load Heatmap', add_help=True)
    parser.add_argument("-f", "--folder",   help="Path to the folder with heatmap files to be refactored", required=True)
    return parser


def get_collected_heatmap_data(folder):
    data = []
    for heatmap_file in os.listdir(folder):
        with open(os.path.join(folder, heatmap_file), 'r') as input_stream:
            heatmap_data = load(input_stream)
        data.append({
            "array":     heatmap_data["data"],
            "bodyarray": [[0] * 300] * len(heatmap_data["data"]),  # dummy data
            "cols":      heatmap_data["columns"],
            "genebody":  [0] * 3000,                               # dummy data
            "glengths":  [5000] * len(heatmap_data["data"]),       # dummy data
            "mapped":    0,                                                            # dummy data
            "max":       max([max(sublist) for sublist in heatmap_data["data"]]),      # dummy data
            "pltname":   heatmap_file,
            "rows":      heatmap_data["index"],
            "rpkmarray": [[10, 12]] * len(heatmap_data["data"]),  # dummy data
            "rpkmcols":  ["RPKM_DUMMY_1", "RPKM_DUMMY_2"],        # dummy data
            "tbl1_id":   "tbl1_id",                               # dummy data
            "tbl1_name": "tbl1_name",                             # dummy data
            "tbl2_id":   "tbl2_id",                               # dummy data
            "tbl2_name": "tbl2_name"                              # dummy data
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