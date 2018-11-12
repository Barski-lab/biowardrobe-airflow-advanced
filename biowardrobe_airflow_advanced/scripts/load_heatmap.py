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
    for json_file in sorted(os.listdir(folder)):
        with open(os.path.join(folder, json_file), 'r') as input_stream:
            json_data = load(input_stream)
        maximum_pos = int(len(json_data["heatmap"]["data"]) * 0.9)
        maximum = sorted([max(sublist) for sublist in json_data["heatmap"]["data"]])[maximum_pos]
        if maximum_pos > 1:
            maximum = maximum + sorted([max(sublist) for sublist in json_data["heatmap"]["data"]])[maximum_pos - 1]
            maximum = maximum / 2.0
        data.append({
            "array":     json_data["heatmap"]["data"],
            "bodyarray": [[0] * 300] * len(json_data["heatmap"]["data"]),  # dummy data
            "cols":      [json_data["heatmap"]["columns"][0]] + [""]*int(len(json_data["heatmap"]["columns"])/2-1) + ["TSS"] + [""]*int(len(json_data["heatmap"]["columns"])/2-1) + [json_data["heatmap"]["columns"][-1]],
            "genebody":  [item[0] for item in json_data["genebody"]["data"]],
            "glengths":  [5000] * len(json_data["heatmap"]["data"]),  # dummy data
            "mapped":    1000000,                                     # dummy data
            "max":       maximum,
            "pltname":   os.path.splitext(os.path.basename(json_file))[0],
            "rows":      json_data["heatmap"]["index"],
            "rpkmarray": [[10, 12]] * len(json_data["heatmap"]["data"]),  # dummy data
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