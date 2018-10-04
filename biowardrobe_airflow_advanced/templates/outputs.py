"""
+----+---------------------------------+----------------------------------+
| id | etype                           | workflow                         |
+----+---------------------------------+----------------------------------+
|  1 | DNA-Seq                         | chipseq-se.cwl                   | SKIP
|  2 | DNA-Seq pair                    | chipseq-pe.cwl                   | SKIP
|  3 | RNA-Seq                         | rnaseq-se.cwl                    |
|  4 | RNA-Seq pair                    | rnaseq-pe.cwl                    |
|  5 | RNA-Seq dUTP                    | rnaseq-se-dutp.cwl               |
|  6 | RNA-Seq dUTP pair               | rnaseq-pe-dutp.cwl               |
|  7 | RNA-Seq dUTP Mitochondrial      | rnaseq-se-dutp-mitochondrial.cwl |
|  8 | DNA-Seq Trim Galore             | trim-chipseq-se.cwl              | SKIP
|  9 | DNA-Seq pair Trim Galore        | trim-chipseq-pe.cwl              | SKIP
| 11 | RNA-Seq dUTP pair Mitochondrial | rnaseq-pe-dutp-mitochondrial.cwl |
+----+---------------------------------+----------------------------------+
"""


DESEQ = {
    "outputs": """{{
        "rpkm_genes": {{
            "class": "File",
            "location": "{raw_data}/{uid}/{uid}.genes.tsv"
        }},
        "rpkm_common_tss": {{
            "class": "File",
            "location": "{raw_data}/{uid}/{uid}.common_tss.tsv"}}
    }}""",
    "script": "Rscript {prefix}/get_gene_n_tss.R {raw_data}/{uid}/{uid}.isoforms.csv {raw_data}/{uid}/{uid}.genes.tsv {raw_data}/{uid}/{uid}.common_tss.tsv"
}




TEMPLATES = {
    3:  [DESEQ],
    4:  [DESEQ],
    5:  [DESEQ],
    6:  [DESEQ],
    7:  [DESEQ],
    11: [DESEQ]
}
