import sumstats.trait.retriever as tr
import sumstats.chr.searcher as chr_searcher
import sumstats.snp.searcher as snp_searcher
import sumstats.utils.argument_utils as au
import argparse
import os.path


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
        return tr.search_study(trait=trait, study=study, start=start, size=size, pval_interval=pval_interval, path=self.path)

    def search_chromosome(self, chromosome, start, size, bp_interval=None, study=None, pval_interval=None):
        h5file = self._get_file_path(dir_name="bychr", file_name=chromosome)
        if not os.path.isfile(h5file):
            return None
        searcher = chr_searcher.Search(h5file)
        if bp_interval is not None:
            searcher.query_chr_for_block_range(chromosome=chromosome, bp_interval=bp_interval, start=start, size=size)
        else:
            searcher.query_for_chromosome(chromosome=chromosome, start=start, size=size)
        result = searcher.get_result()
        searcher.close_file()
        return result

    def search_snp(self, snp, start, size, study=None, pval_interval=None):
        for chromosome in range(1, 23):
            h5file = self._get_file_path(dir_name="bysnp", file_name=chromosome)
            if not os.path.isfile(h5file):
                continue
            searcher = snp_searcher.Search(h5file)
            if searcher.snp_in_file(snp):
                searcher.query_for_snp(snp=snp, start=start, size=size)
                result = searcher.get_result()
                searcher.close_file()
                return result

        return None

    def _get_file_path(self, dir_name, file_name):
        return self.path + "/" + dir_name + "/file_" + str(file_name) + ".h5"


def main():

    args = argument_parser()

    trait, study, chromosome, bp_interval, snp, pval_interval = au.convert_search_args(args)
    path = args.path
    fins_all = args.all
    start = args.start
    if start is None:
        start = 0
    else:
        start = int(start)
    size = args.size
    if size is None:
        size = 20
    else:
        size = int(size)

    search = Search(path)

    if fins_all:
        result = search.search_all_assocs(start=start, size=size, pval_interval=pval_interval)
    elif trait is not None:
        if study is not None:
            result = search.search_study(trait=trait, study=study, start=start, size=size, pval_interval=pval_interval)
        else:
            result = search.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)

    elif chromosome is not None:
        result = search.search_chromosome(chromosome=chromosome, start=start, size=size, bp_interval=bp_interval, study=study, pval_interval=pval_interval)

    elif snp is not None:
        result = search.search_snp(snp=snp, start=start, size=size, study=study, pval_interval=pval_interval)
    else:
        raise ValueError("Input is wrong!")

    if result is not None:
        for name, dataset in result.items():
            print(name, dataset)
    else:
        print("Result is empty!")


if __name__ == "__main__":
    main()


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', help='Full path to the dir where the h5files will be stored')
    parser.add_argument('-all', action='store_true', help='Use argument if you want to search for all associations')
    parser.add_argument('-start', help='Index of the first association retrieved')
    parser.add_argument('-size', help='Number of retrieved associations')
    parser.add_argument('-trait', help='The trait I am looking for')
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-snp', help='The SNP I am looking for')
    parser.add_argument('-chr', help='The chromosome I am looking for')
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')
    parser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')

    return parser.parse_args()