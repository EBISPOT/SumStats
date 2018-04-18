import csv
from sumstats.common_constants import *


sumstat_header_transformations = {

    # variant id
    'snp': SNP_DSET,
    # p-value
    'pval': PVAL_DSET,
    # chromosome
    'chr': CHR_DSET, 
    # base pair location
    'bp': BP_DSET, 
    # odds ratio
    'or': OR_DSET,
    # or range
    'range': RANGE_DSET,
    # beta
    'beta': BETA_DSET,
    # standard error
    'se': SE_DSET,
    # effect allele
    'effect_allele': EFFECT_DSET,
    # other allele
    'other_allele': OTHER_DSET,
    # effect allele frequency
    'eaf': FREQ_DSET
}


def refactor_header(header):
    return [sumstat_header_transformations[h] if h in sumstat_header_transformations else h for h in header]


def mapped_headers(header):
    return {h: sumstat_header_transformations[h] for h in header if h in sumstat_header_transformations}


def missing_headers(header):
    return [h for h in sumstat_header_transformations.values() if h not in header]


def get_csv_reader(csv_file):
    dialect = csv.Sniffer().sniff(csv_file.readline())
    csv_file.seek(0)
    return csv.reader(csv_file, dialect)


def get_filename(file):
    return file.split("/")[-1].split(".")[0]
