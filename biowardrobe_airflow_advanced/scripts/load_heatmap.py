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
            "genebody":  [item[3] for item in json_data["genebody"]["data"]],
            "glengths":  [idx[4] - idx[3] for idx in json_data["rpkm"]["index"]],
            "mapped":    1000000,                                     # dummy data
            "max":       maximum,
            "pltname":   json_data["plot_name"],
            "rows":      json_data["heatmap"]["index"],               # maybe I should take it from json_data["rpkm"]["index"]
            "rpkmarray": json_data["rpkm"]["data"],
            "rpkmcols":  json_data["rpkm"]["columns"],
            "tbl1_id":   json_data["data_uid"],
            "tbl1_name": json_data["data_name"],
            "tbl2_id":   json_data["intervals_uid"],
            "tbl2_name": json_data["intervals_name"]
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