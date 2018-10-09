"""Strategy pattern to run BaseUploader.execute depending on types of files to be uploaded"""
import logging

from biowardrobe_airflow_advanced.utils.connect import HookConnect
from biowardrobe_airflow_advanced.utils.analyze import get_genelist_data


logger = logging.getLogger(__name__)


def update_deseq_genelist(conf):
    logger.debug(f"Updating genelist table with DESeq results for {conf['uid']}")
    connect_db = HookConnect()
    genelist_info = [get_genelist_data(uid) for uid in conf['condition']]

    grouping = {1: "isoforms", 2: "genes", 3: "common tss"}[conf["groupby"]]
    gblink = "&".join([item["gblink"] for item in genelist_info])
    names = [item["name"] for item in genelist_info]
    table_name = conf["uid"].replace("-","")
    comment = f"""Annotation grouping ({grouping}) were used for DESeq analysis.<br>Data from "{names[0]}" vs "{names[1]}" has been chosen."""

    sql_header = f"""INSERT INTO genelist (id,name,leaf,`type`,conditions,gblink,db,tableName,rtype_id,project_id) VALUES
                     ('{conf["uid"]}',
                      '{conf["name"]}',
                       1,
                       3,
                      '{comment}',
                      '{gblink}',
                      '',
                      '{table_name}',
                       {conf["groupby"]},
                      '{conf["project_uid"]}')"""
    connect_db.execute(sql_header)


def upload_deseq_results(uid, filename, clean=False):
    connect_db = HookConnect()
    table_name = connect_db.get_settings_data()["experimentsdb"] + '.`' + uid.replace("-", "") + '`'
    logger.debug(f"Uploading DESeq results from file {filename} to {table_name}")
    connect_db.execute(f"DROP TABLE IF EXISTS {table_name}")
    logger.debug(f"Drop {table_name} if exist")
    if not clean:
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
