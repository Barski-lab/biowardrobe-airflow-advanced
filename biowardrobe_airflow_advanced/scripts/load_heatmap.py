#! /usr/bin/env python3
import sys
import logging
from json import dumps, loads, load

from biowardrobe_airflow_advanced.utils.connect import HookConnect


logger = logging.getLogger(__name__)


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


def get_collect_heatmap_data(uid):
    data = []
    for atdp_data in get_atdp_data(uid):
        for heatmap_file in atdp_data["outputs"]["heatmap_file"]:
            heatmap_data = load(heatmap_file["lcoation"])
            data.append({
                "array":     heatmap_data["data"],
                "rows":      heatmap_data["index"],
                "cols":      heatmap_data["columns"],
                "pltname":   atdp_data["name"],
                "tbl1_id":   atdp_data["data_uid"],
                "tbl2_id":   atdp_data["intervals_uid"],
                "bodyarray": [],
                "genebody":  [],
                "rpkmarray": [],
                "rpkmcols":  [],
                "glengths" : [],
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


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    print(dumps(get_collect_heatmap_data(args[1]), indent=4))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))