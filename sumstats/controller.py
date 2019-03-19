import argparse
import sys

import sumstats.chr.retriever as cr
import sumstats.snp.retriever as snpr
import sumstats.trait.retriever as tr
import sumstats.utils.argument_utils as au
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties
import sumstats.explorer as ex
import sumstats.utils.sqlite_client as sql_client



class Search(object):
    def __init__(self, config_properties=None):
        self.config_properties = config_properties
        #self.sqlite_db = properties.sqlite_path

    def search(self, start, size, pval_interval=None, study=None, trait=None,
               chromosome=None, bp_interval=None, tissue=None, snp=None):
        return cr.search_all_assocs(start=start, size=size, pval_interval=pval_interval,
                                    properties=self.config_properties, study=study, trait=trait,
                                    chromosome=chromosome, bp_interval=bp_interval, tissue=tissue, snp=snp)

def main():  # pragma: no cover
    args = argument_parser(sys.argv[1:])  # pragma: no cover

    trait, study, chromosome, bp_interval, snp, pval_interval, tissue = au.convert_search_args(args)  # pragma: no cover

    find_all = args.all  # pragma: no cover
    start = args.start  # pragma: no cover
    if start is None:  # pragma: no cover
        start = 0
    else:
        start = int(start)
    size = args.size  # pragma: no cover
    if size is None:  # pragma: no cover
        size = 20
    else:
        size = int(size)

    search = Search(properties)  # pragma: no cover

    if find_all:  # pragma: no cover
        result, index_marker = search.search(start=start, size=size, pval_interval=pval_interval)

    elif any([trait, study, chromosome, bp_interval, snp, pval_interval, tissue]):
        result, index_marker = search.search(start=start, size=size, pval_interval=pval_interval,
                                             study=study, trait=trait, chromosome=chromosome,
                                             bp_interval=bp_interval, tissue=tissue, snp=snp)

    else:
        raise ValueError("Input is wrong!")

    if result is not None:  # pragma: no cover
        for name, dataset in result.items():
            print(name, dataset)
    else:
        print("Result is empty!")

if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-path', help='Full path to the dir where the h5files will be stored')  # pragma: no cover
    parser.add_argument('-all', action='store_true',
                        help='Use argument if you want to search for all associations')  # pragma: no cover
    parser.add_argument('-start', help='Index of the first association retrieved')  # pragma: no cover
    parser.add_argument('-size', help='Number of retrieved associations')  # pragma: no cover
    parser.add_argument('-trait', help='The trait I am looking for')  # pragma: no cover
    parser.add_argument('-study', help='The study I am looking for')  # pragma: no cover
    parser.add_argument('-tissue', help='The tissue I am looking for')  # pragma: no cover
    parser.add_argument('-snp', help='The SNP I am looking for')  # pragma: no cover
    parser.add_argument('-chr', help='The chromosome I am looking for')  # pragma: no cover
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')  # pragma: no cover
    parser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')  # pragma: no cover

    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover
