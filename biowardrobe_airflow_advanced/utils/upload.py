"""Strategy pattern to run BaseUploader.execute depending on types of files to be uploaded"""
import logging

from biowardrobe_airflow_advanced.utils.connect import HookConnect


logger = logging.getLogger(__name__)


def upload_deseq(uid, filename, clean=False):
    connect_db = HookConnect()
    table_name = connect_db.get_settings_data()["experimentsdb"] + '.`' + uid + '`'
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
