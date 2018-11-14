"""Strategy pattern to run BaseUploader.execute depending on types of files to be uploaded"""
import logging
from json import dumps, load

from biowardrobe_airflow_advanced.utils.connect import HookConnect
from biowardrobe_airflow_advanced.utils.analyze import get_genelist_data
from biowardrobe_airflow_advanced.utils.utilities import strip_filepath


logger = logging.getLogger(__name__)


def update_atdp_table_for_heatmap(conf, job_result):
    logger.debug(f"Updating atdp table with Heatmap results for {conf['uid']}")
    connect_db = HookConnect()
    connect_db.execute(f"""UPDATE atdp
                           SET params='{dumps(job_result)}'
                           WHERE genelist_id='{conf["uid"]}' AND
                                 tbl1_id='{conf["data_uid"]}' AND
                                 tbl2_id='{conf["intervals_uid"]}' AND
                                 pltname='{conf["name"]}'""")


def upload_atdp_results(conf, job_result):
    connect_db = HookConnect()
    filename = strip_filepath(job_result["json_file"]["location"])
    table_name = connect_db.get_settings_data()["experimentsdb"] + '.`' + conf["uid"] + '`'
    logger.debug(f"Uploading ATDP results from file {filename} to {table_name}")
    atdp_tables = connect_db.fetchall(f"""SELECT tbl1_id,tbl2_id,pltname
                                          FROM atdp
                                          WHERE genelist_id='{conf["uid"]}'
                                          ORDER BY tbl1_id, tbl2_id""")  # we need this to display results in correct order
    idx = atdp_tables.index({"tbl1_id": conf["data_uid"],
                             "tbl2_id": conf["intervals_uid"],
                             "pltname": conf["name"]})

    with open(filename, 'r') as input_stream:
        atdp_data = load(input_stream)["atdp"]

    if not connect_db.fetchone(f"""SHOW TABLES FROM {connect_db.get_settings_data()["experimentsdb"]} like '{conf["uid"]}'"""):
        y_columns = ", ".join(["Y{} FLOAT NULL".format(i) for i in range(len(atdp_tables))])
        connect_db.execute(f"""CREATE TABLE {table_name}
                               ( 
                                 X INT NULL,
                                 {y_columns},
                                 INDEX X_idx (X) using btree
                               )
                               ENGINE=MyISAM DEFAULT CHARSET=utf8""")
        logger.debug(f"Create {table_name}")
        for x_coord, data_record in zip(atdp_data["index"], atdp_data["data"]):
            connect_db.execute(f"""INSERT INTO {table_name} (X, Y{idx}) VALUES ({x_coord}, {data_record[3]})""")
    else:
        for x_coord, data_record in zip(atdp_data["index"], atdp_data["data"]):
            # data_record[3] corresponds to "smooth" column of "convert_to_json" generated file for "atdp"
            connect_db.execute(f"""UPDATE {table_name} SET Y{idx}={data_record[3]} WHERE X={x_coord}""")
    logger.debug(f"Insert data into {table_name}")


def update_genelist_table_for_deseq(conf, job_result):
    logger.debug(f"Updating genelist table with DESeq results for {conf['uid']}")
    connect_db = HookConnect()
    genelist_info = [get_genelist_data(uid) for uid in conf['condition']]

    grouping = {1: "isoforms", 2: "genes", 3: "common tss"}[conf["groupby"]]
    gblink = "&".join([item["gblink"] for item in genelist_info])
    names = [item["name"] for item in genelist_info]
    table_name = conf["uid"].replace("-","")
    comment = f"""Annotation grouping ({grouping}) were used for DESeq analysis.<br>Data from "{names[0]}" vs "{names[1]}" has been chosen."""

    sql_header = f"""INSERT INTO genelist (id,name,leaf,`type`,conditions,gblink,db,tableName,rtype_id,project_id,params) VALUES
                     ('{conf["uid"]}',
                      '{conf["name"]}',
                       1,
                       3,
                      '{comment}',
                      '{gblink}',
                      '',
                      '{table_name}',
                       {conf["groupby"]},
                      '{conf["project_uid"]}',
                      '{dumps(job_result)}')"""
    connect_db.execute(sql_header)


def update_genelist_table_for_atdp(conf):
    logger.debug(f"Updating genelist table with ATDP results for {conf['uid']}")
    connect_db = HookConnect()
    connect_db.execute(f"""UPDATE genelist SET tableName={conf['uid']} WHERE id={conf['uid']}""")


def upload_deseq_results(conf, job_result):
    connect_db = HookConnect()
    filename = strip_filepath(job_result["diff_expr_file"]["location"])
    table_name = connect_db.get_settings_data()["experimentsdb"] + '.`' + conf["uid"].replace("-", "") + '`'
    logger.debug(f"Uploading DESeq results from file {filename} to {table_name}")
    connect_db.execute(f"DROP TABLE IF EXISTS {table_name}")
    logger.debug(f"Drop {table_name} if exist")
    with open(filename, 'r') as input_file:
        header = input_file.readline().strip().split()
    u_rpkm, t_rpkm = header[6], header[7]
    connect_db.execute(f"""CREATE TABLE {table_name}
                             (refseq_id VARCHAR(1000) NOT NULL,
                             gene_id VARCHAR(500) NOT NULL,
                             chrom VARCHAR(45) NOT NULL,
                             txStart INT NULL,
                             txEnd INT NULL,
                             strand VARCHAR(1),
                             {u_rpkm} FLOAT,
                             {t_rpkm} FLOAT,
                             LOGR FLOAT,
                             pvalue FLOAT,
                             padj FLOAT,
                             INDEX refseq_id_idx (refseq_id ASC) USING BTREE,
                             INDEX gene_id_idx (gene_id ASC) USING BTREE,
                             INDEX chr_idx (chrom ASC) USING BTREE,
                             INDEX txStart_idx (txStart ASC) USING BTREE,
                             INDEX txEnd_idx (txEnd ASC) USING BTREE
                            ) ENGINE=MyISAM DEFAULT CHARSET=utf8 """)
    logger.debug(f"Create {table_name}")
    sql_header = f"INSERT INTO {table_name} VALUES "
    value_list = []
    with open(filename, 'r') as input_file:
        for line in input_file.read().splitlines():
            # RefseqId, GeneId, Chrom, TxStart, TxEnd, Strand, uRpkm, tRpkm, log2FoldChange, pvalue, padj
            if not line or "RefseqId" in line or "GeneId" in line:
                continue
            value_list.append("('{}','{}','{}',{},{},'{}',{},{},{},{},{})".format(*line.split()))
    connect_db.execute(sql_header + ",".join(value_list))
    logger.debug(f"Insert data into {table_name}")
