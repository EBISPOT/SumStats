import argparse
from sumstats.utils.interval import *


def search_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', help='The location of the h5files')
    parser.add_argument('-h5file', help='The name of the HDF5 file')
    parser.add_argument('-trait', help='The trait I am looking for')
    parser.add_argument('-gene', help='The gene I am looking for')
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-qtl_group', help='The QTL group/context I am looking for')
    parser.add_argument('-snp', help='Filter by SNP')
    parser.add_argument('-chr', help='Filter by chromosome')
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')
    parser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')
    parser.add_argument('-tissue', help='The tissue I am looking for')
    parser.add_argument('-quant_method', help='The quantification method')
    parser.add_argument('-paginate', help='Set paginate to "False" if you would like to fetch all associations for your query')

    return parser.parse_args()


def convert_search_args(args):
    """
    Converts arguments passed by the user from string to what they need to be (int, float interval, etc)
    :param args: the raw arguments passed by the user and that where
    :return: the converted arguments in their correct form
    """
    trait = args.trait
    gene = args.gene
    study = args.study
    snp = args.snp
    tissue = args.tissue
    qtl_group = args.qtl_group
    quant_method = args.quant_method
    paginate = args.paginate

    chromosome = args.chr
    if chromosome is not None:
        chromosome = int(chromosome)

    pval_interval = args.pval
    pval_interval = FloatInterval().set_string_tuple(pval_interval)

    bp_interval = args.bp
    bp_interval = IntInterval().set_string_tuple(bp_interval)

    return trait, gene, study, chromosome, bp_interval, snp, pval_interval, tissue, quant_method, paginate, qtl_group


def load_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help='The file to be loaded')
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated')
    parser.add_argument('-study', help='The name of the first group this will belong to', required=True)
    parser.add_argument('-trait', help='The name of the trait the SNPs of this file are related to')
    parser.add_argument('-loader', help='The type of loader: [trait|chr|snp]')
    parser.add_argument('-chr', help='The chromosome that will be loaded')
    parser.add_argument('-tsvfiles_path', help='The path of the input files')
    parser.add_argument('-h5files_path', help='The path of the output files')

    return parser.parse_args()


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
