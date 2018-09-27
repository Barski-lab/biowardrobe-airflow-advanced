"""Strategy pattern to run BaseUploader.execute depending on types of files to be uploaded"""
import logging
from biowardrobe_airflow_advanced.utils.connect import HookConnect


logger = logging.getLogger(__name__)


def upload_deseq(uid, filename, clean=False):
    logger.debug(f"Processing TSV file: {filename}")
    connect_db = HookConnect()
    table_name = connect_db.get_settings["experimentsdb"] + '.`' + uid + '`'
    logger.debug(f"Drop table {table_name}")
    connect_db.execute(f"DROP TABLE IF EXISTS {table_name}")
    connect_db.execute(f"DROP VIEW IF EXISTS {table_name}")
    if not clean:
        logger.debug(f"Create table {table_name}")
        connect_db.execute(f"""CREATE TABLE {table_name}
                                 (refseq_id VARCHAR(100) NOT NULL,
                                 gene_id VARCHAR(100) NOT NULL,
                                 chrom VARCHAR(255) NOT NULL,
                                 txStart INT NULL,
                                 txEnd INT NULL,
                                 strand VARCHAR(1),
                                 TOT_R_0 FLOAT,
                                 RPKM_0 FLOAT
                                ) ENGINE=MyISAM DEFAULT CHARSET=utf8 """)
        SQL = f"INSERT INTO {table_name} (refseq_id,gene_id,chrom,txStart,txEnd,strand,TOT_R_0,RPKM_0) VALUES"
        with open(filename, 'r') as input_file:
            for line in input_file.read().splitlines():
                # RefseqId, GeneId, Chrom, TxStart, TxEnd, Strand, TotalReads, Rpkm
                if not line or "RefseqId" in line or "GeneId" in line:
                    continue
                connect_db.execute(SQL + " (%s,%s,%s,%s,%s,%s,%s,%s)", tuple(line.split(',')))