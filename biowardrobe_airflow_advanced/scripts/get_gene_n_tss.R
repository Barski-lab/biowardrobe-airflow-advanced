#!/usr/bin/env Rscript
options(warn=-1)

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

args <- commandArgs(trailingOnly = TRUE)
isoforms <- normalizePath(as.character(args[1]))
gene <- as.character(args[2])
tss <- as.character(args[3])

if(is.na(gene) || is.na(tss)){
    isoforms_nameroot = head(unlist(strsplit(basename(isoforms), ".", fixed = TRUE)), 1)
    gene <- paste(isoforms_nameroot, "genes.tsv", sep=".")
    tss <- paste(isoforms_nameroot, "common_tss.tsv", sep=".")
}

# Group by gene and common tss
column_order <- c("RefseqId","GeneId","Chrom","TxStart","TxEnd","Strand","TotalReads","Rpkm")
gene_data <- load_isoform(isoforms, "gene")[column_order]
tss_data <- load_isoform(isoforms, "tss")[column_order]


# Export results to TSV files
write.table(gene_data, file=gene, sep="\t", row.names=FALSE, col.names=TRUE, quote=FALSE)
write.table(tss_data,  file=tss,  sep="\t", row.names=FALSE, col.names=TRUE, quote=FALSE)
