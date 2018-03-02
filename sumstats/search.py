import argparse

import sumstats.chr.retriever as cr
import sumstats.snp.retriever as snpr
import sumstats.trait.retriever as tr
import sumstats.utils.argument_utils as au


class Search:
    def __init__(self, path=None):
        if path is None:
            print("Search: setting default location for output files")
            path = "/output"

        self.path = path

    def search_all_assocs(self, start, size, pval_interval=None):
        return tr.search_all_assocs(start=start, size=size, pval_interval=pval_interval, path=self.path)

    def search_trait(self, trait, start, size, pval_interval=None):
        return tr.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval, path=self.path)

    def search_study(self, trait, study, start, size, pval_interval=None):
        return tr.search_study(trait=trait, study=study, start=start, size=size, pval_interval=pval_interval,
                               path=self.path)

    def search_chromosome(self, chromosome, start, size, bp_interval=None, study=None, pval_interval=None):
        return cr.search_chromosome(chromosome=chromosome, start=start, size=size, path=self.path,
                                    bp_interval=bp_interval, study=study, pval_interval=pval_interval)

    def search_snp(self, snp, start, size, chromosome=None, study=None, pval_interval=None):
        return snpr.search_snp(snp=snp, chromosome=chromosome, start=start, size=size, study=study,
                               pval_interval=pval_interval, path=self.path)


def main():  # pragma: no cover

    args = argument_parser()  # pragma: no cover

    trait, study, chromosome, bp_interval, snp, pval_interval = au.convert_search_args(args)  # pragma: no cover
    path = args.path  # pragma: no cover
    fins_all = args.all  # pragma: no cover
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

    search = Search(path)  # pragma: no cover

    if fins_all:  # pragma: no cover
        result = search.search_all_assocs(start=start, size=size, pval_interval=pval_interval)
    elif trait is not None:
        if study is not None:
            result = search.search_study(trait=trait, study=study, start=start, size=size, pval_interval=pval_interval)
        else:
            result = search.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)

    elif chromosome is not None:
        if snp is not None:
            result = search.search_snp(snp=snp, start=start, size=size, study=study, pval_interval=pval_interval)
        else:
            result = search.search_chromosome(chromosome=chromosome, start=start, size=size, bp_interval=bp_interval,
                                              study=study, pval_interval=pval_interval)
    else:
        raise ValueError("Input is wrong!")

    if result is not None:  # pragma: no cover
        for name, dataset in result.items():
            print(name, dataset)
    else:
        print("Result is empty!")


if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser():
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-path', help='Full path to the dir where the h5files will be stored')  # pragma: no cover
    parser.add_argument('-all', action='store_true',
                        help='Use argument if you want to search for all associations')  # pragma: no cover
    parser.add_argument('-start', help='Index of the first association retrieved')  # pragma: no cover
    parser.add_argument('-size', help='Number of retrieved associations')  # pragma: no cover
    parser.add_argument('-trait', help='The trait I am looking for')  # pragma: no cover
    parser.add_argument('-study', help='The study I am looking for')  # pragma: no cover
    parser.add_argument('-snp', help='The SNP I am looking for')  # pragma: no cover
    parser.add_argument('-chr', help='The chromosome I am looking for')  # pragma: no cover
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')  # pragma: no cover
    parser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')  # pragma: no cover

    return parser.parse_args()  # pragma: no cover
