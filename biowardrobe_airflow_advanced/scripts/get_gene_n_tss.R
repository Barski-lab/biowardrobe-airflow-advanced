#!/usr/bin/env Rscript
options(warn=-1)
options("width"=200)


suppressMessages(library(argparse))
suppressMessages(library(data.table))


##########################################################################################
# v0.0.1
# Input CSV isoform expression file should have the following header (case-sensitive)
# <RefseqId,GeneId,Chrom,TxStart,TxEnd,Strand,TotalReads,Rpkm>
# Order of the rows in the output files is not guaranted
##########################################################################################


load_isoform <- function(filename, combine_type) {
    isoforms <- setDT(read.table(filename, sep=",", header=TRUE, stringsAsFactors=FALSE))
    if (combine_type == "gene") {
        isoforms <- isoforms[, .(RefseqId = paste(sort(unique(RefseqId)), collapse = ","),
                                 Chrom = max(Chrom),
                                 TxStart = max(TxStart),
                                 TxEnd = max(TxEnd),
                                 Strand = max(Strand),
                                 TotalReads = sum(TotalReads),
                                 Rpkm = sum(Rpkm)),
                             by = GeneId]
    } else if (combine_type == "tss") {
        isoforms_upstream <- isoforms[Strand=="+", .(RefseqId = paste(sort(unique(RefseqId)), collapse = ","),
                                                     GeneId = paste(sort(unique(GeneId)), collapse = ","),
                                                     TxEnd = max(TxEnd),
                                                     TotalReads = sum(TotalReads),
                                                     Rpkm = sum(Rpkm)),
                                      by = .(Chrom, TxStart, Strand)]
        isoforms_downstream <- isoforms[Strand=="-", .(RefseqId = paste(sort(unique(RefseqId)), collapse = ","),
                                                       GeneId = paste(sort(unique(GeneId)), collapse = ","),
                                                       TxStart = min(TxStart),
                                                       TotalReads = sum(TotalReads),
                                                       Rpkm = sum(Rpkm)),
                                        by = .(Chrom, TxEnd, Strand)]
        isoforms <- rbind(isoforms_upstream, isoforms_downstream)
    }
    return(as.data.frame(isoforms))
}


# Parser
parser <- ArgumentParser(description='Group isoform expression data by gene and common TSS')
parser$add_argument("-i", "--isoforms",  help='Input CSV isoform expression file',     type="character", required="True")
parser$add_argument("-g", "--gene",      help='Output TSV gene expression file',       type="character", default="gene.tsv")
parser$add_argument("-t", "--tss",       help='Output TSV common tss expression file', type="character", default="tss.tsv")
args <- parser$parse_args(commandArgs(trailingOnly = TRUE))


# Group by gene and common tss
column_order <- c("RefseqId","GeneId","Chrom","TxStart","TxEnd","Strand","TotalReads","Rpkm")
gene_data <- load_isoform(args$isoforms, "gene")[column_order]
tss_data <- load_isoform(args$isoforms, "tss")[column_order]


# Export results to TSV files
write.table(gene_data, file=args$gene, sep="\t", row.names=FALSE, col.names=TRUE, quote=FALSE)
write.table(tss_data,  file=args$tss,  sep="\t", row.names=FALSE, col.names=TRUE, quote=FALSE)
