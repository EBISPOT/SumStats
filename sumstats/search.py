import sumstats.trait.searcher as trait_searcher
import sumstats.chr.searcher as chr_searcher
import sumstats.snp.searcher as snp_searcher
import sumstats.utils.argument_utils as au
import sumstats.explorer as ex
from sumstats.trait.constants import *
import sumstats.utils.utils as utils
import argparse
import os.path


class Search:
    def __init__(self, path=None):
        if path is None:
            print("Search: setting default location for output files")
            path = ""

        self.output_path = path + "/output"

    def search_all_assocs(self, start, size, snp=None, chromosome=None, pval_interval=None, bp_interval=None):
        datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        trait_list = []
        print("Searching for all associations!")
        explorer = ex.Explorer()
        available_traits = explorer.get_list_of_traits()
        all_groups_size = 0

        for trait in available_traits:
            print("searching trait:", trait)
            h5file = self.output_path + "/bytrait/file_" + trait + ".h5"
            if os.path.isfile(h5file):
                searcher = trait_searcher.Search(h5file)
                searcher.query_for_trait(trait, start, size)
                searcher.apply_restrictions(snp=snp, chromosome=chromosome, pval_interval=pval_interval,
                                            bp_interval=bp_interval)
                result = searcher.get_result()
                searcher.close_file()
                dset_size = len(result[REFERENCE_DSET])

                all_groups_size += dset_size
                if dset_size == 0:
                    searcher = trait_searcher.Search(h5file)
                    searcher.query_for_trait(trait, 0, start)
                    searcher.apply_restrictions(snp=snp, chromosome=chromosome, pval_interval=pval_interval,
                                                bp_interval=bp_interval)
                    tmp_result = searcher.get_result()
                    searcher.close_file()
                    all_groups_size += len(tmp_result[REFERENCE_DSET])

                trait_list.extend([trait for _ in range(dset_size)])
                for dset_name, dataset in datasets.items():
                    dataset.extend(result[dset_name])

                if size <= dset_size:
                    datasets['trait'] = trait_list
                    return datasets
                else:
                    retrieved_size = len(result[REFERENCE_DSET])

                    size = size - retrieved_size
                    start = start - all_groups_size + retrieved_size
                    continue

        return datasets

    def search_trait(self, trait, start, size, snp=None, chromosome=None, pval_interval=None, bp_interval=None):
        result = None
        print("Searching for Trait!")
        h5file = self.output_path + "/bytrait/file_" + trait + ".h5"
        if os.path.isfile(h5file):
            searcher = trait_searcher.Search(h5file)
            searcher.query_for_trait(trait, start, size)
            searcher.apply_restrictions(snp=snp, chromosome=chromosome, pval_interval=pval_interval, bp_interval=bp_interval)
            result = searcher.get_result()
            searcher.close_file()
        return result

    def search_study(self, trait, study, start, size, snp=None, chromosome=None, pval_interval=None, bp_interval=None):
        result = None
        print("Searching for Study!")
        h5file = self.output_path + "/bytrait/file_" + trait + ".h5"
        if os.path.isfile(h5file):
            searcher = trait_searcher.Search(h5file)
            searcher.query_for_study(trait, study, start, size)

            searcher.apply_restrictions(snp=snp, chromosome=chromosome, pval_interval=pval_interval, bp_interval=bp_interval)
            result = searcher.get_result()
            searcher.close_file()
        return result

    def search_chromosome(self, chromosome, start, size, bp_interval=None, study=None, pval_interval=None):
        result = None
        print("Searching for CHROMOSOME!")
        h5file = self.output_path + "/bychr/file_" + str(chromosome) + ".h5"
        if os.path.isfile(h5file):
            searcher = chr_searcher.Search(h5file)
            if bp_interval is not None:
                searcher.query_chr_for_block_range(chromosome, bp_interval, start, size)
            else:
                searcher.query_for_chromosome(chromosome, start, size)
            searcher.apply_restrictions(study=study, pval_interval=pval_interval)
            result = searcher.get_result()
            searcher.close_file()
        return result

    def search_snp(self, snp, start, size, study=None, pval_interval=None):
        result = None
        print("Searching for SNP!")
        for chromosome in range(1, 23):
            h5file = self.output_path + "/bysnp/file_" + str(chromosome) + ".h5"
            print("file", h5file)
            if os.path.isfile(h5file):
                searcher = snp_searcher.Search(h5file)
                if searcher.snp_in_file(snp):
                    searcher.query_for_snp(snp, start, size)
                    searcher.apply_restrictions(study=study, pval_interval=pval_interval)
                    result = searcher.get_result()
                    searcher.close_file()
                    return result

        return result


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
        result = search.search_all_assocs(start, size, snp, chromosome, pval_interval, bp_interval)
    elif trait is not None:
        if study is not None:
            result = search.search_study(trait, study, start, size, snp, chromosome, pval_interval, bp_interval)
        else:
            result = search.search_trait(trait, start, size, snp, chromosome, pval_interval, bp_interval)

    elif chromosome is not None:
        result = search.search_chromosome(chromosome, start, size, bp_interval, study, pval_interval)

    elif snp is not None:
        result = search.search_snp(snp, start, size, study, pval_interval)
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
    parser.add_argument('-path', help='The path to the parent of the \'output\' dir where the h5files are stored')
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