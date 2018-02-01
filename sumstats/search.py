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

        self.path = path
        self.output_path = path + "/output"

    def search_all_assocs(self, start, size, pval_interval=None):
        
        datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        trait_list = []
        available_traits = self._get_all_traits()
        search_traversed = overall_search_index = 0
        starting_point = start
        
        for trait in available_traits:
            h5file = self._get_file_path(dir_name="bytrait", file_name=trait)
            if not os.path.isfile(h5file):
                continue
            
            result, current_trait_index = self._search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)
            overall_search_index += current_trait_index
            currently_retrieved = len(result[REFERENCE_DSET])

            search_traversed += self._get_traversed_size(retrieved_index=current_trait_index, trait=trait)
            datasets = utils.extend_dsets_with_subset(datasets, result)
            trait_list.extend([trait for _ in range(currently_retrieved)])
            total_retrieved = len(datasets[REFERENCE_DSET])

            if size <= total_retrieved:
                datasets['trait'] = trait_list
                return datasets, starting_point + overall_search_index
            else:
                size = size - currently_retrieved
                start = self._next_start_index(current_search_index=current_trait_index, total_traversed=search_traversed, start=start)

        return datasets, starting_point + overall_search_index

    def _get_all_traits(self):
        explorer = ex.Explorer(self.path)
        return explorer.get_list_of_traits()

    def _get_traversed_size(self, retrieved_index, trait):
        if retrieved_index == 0:
            h5file = self._get_file_path(dir_name="bytrait", file_name=trait)
            searcher = trait_searcher.Search(h5file)
            trait_size = searcher.get_trait_size(trait)
            searcher.close_file()
            return trait_size
        return retrieved_index

    @staticmethod
    def _next_start_index(current_search_index, total_traversed, start):
        if current_search_index == total_traversed:
            # we have retrieved the trait from start to end
            # retrieving next trait from it's beginning
            return 0
        return start - total_traversed + current_search_index

    def search_trait(self, trait, start, size, pval_interval=None):
        h5file = self._get_file_path(dir_name="bytrait", file_name=trait)
        if not os.path.isfile(h5file):
            return None
        return self._search_trait(trait=trait, start=start, size=size)

    def _search_trait(self, trait, start, size, pval_interval=None):
        h5file = self._get_file_path(dir_name="bytrait", file_name=trait)
        searcher = trait_searcher.Search(h5file)

        gather_results = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        total_size_searched = 0
        max_size_of_trait = searcher.get_trait_size(trait)
        search_size_of_iteration = size

        while start < max_size_of_trait:
            searcher.query_for_trait(trait=trait, start=start, size=search_size_of_iteration)
            total_size_searched += len(searcher.get_result()[REFERENCE_DSET])

            searcher.apply_restrictions(pval_interval=pval_interval)

            result = searcher.get_result()
            gather_results = utils.extend_dsets_with_subset(gather_results, result)
            start = start + size
            search_size_of_iteration = size - len(gather_results[REFERENCE_DSET])
            if len(gather_results[REFERENCE_DSET]) >= size:
                break

        searcher.close_file()
        return gather_results, total_size_searched

    def search_study(self, trait, study, start, size, snp=None, chromosome=None, pval_interval=None, bp_interval=None):
        h5file = self._get_file_path(dir_name="bytrait", file_name=trait)
        if not os.path.isfile(h5file):
            return None
        searcher = trait_searcher.Search(h5file)
        searcher.query_for_study(trait=trait, study=study, start=start, size=size)

        result = searcher.get_result()
        searcher.close_file()
        return result

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
        return self.output_path + "/" + dir_name + "/file_" + str(file_name) + ".h5"


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
            result = search.search_study(trait=trait, study=study, start=start, size=size, snp=snp, chromosome=chromosome, pval_interval=pval_interval, bp_interval=bp_interval)
        else:
            result = search.search_trait(trait=trait, start=start, size=size, snp=snp, chromosome=chromosome, pval_interval=pval_interval, bp_interval=bp_interval)

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