import sumstats.trait.searcher as trait_searcher
import sumstats.chr.searcher as chr_searcher
import sumstats.snp.searcher as snp_searcher
import sumstats.utils.argument_utils as au
import argparse
import os.path


class Search():
    def __init__(self, path=None):
        if path is None:
            print("Setting default location for output files")
            path = ""

        self.output_path = path + "/output"

    def search_trait(self, trait, snp=None, chromosome=None, pval_interval=None, bp_interval=None):
        result = None
        print("Searching for Trait!")
        h5file = self.output_path + "/bytrait/file_" + trait + ".h5"
        if os.path.isfile(h5file):
            searcher = trait_searcher.Search(h5file)
            searcher.query_for_trait(trait)

            searcher.apply_restrictions(snp=snp, chr=chromosome, pval_interval=pval_interval, bp_interval=bp_interval)
            result = searcher.get_result()
        return result

    def search_study(self, trait, study, snp=None, chromosome=None, pval_interval=None, bp_interval=None):
        result = None
        print("Searching for Study!")
        h5file = self.output_path + "/bytrait/file_" + trait + ".h5"
        if os.path.isfile(h5file):
            searcher = trait_searcher.Search(h5file)
            searcher.query_for_study(trait, study)

            searcher.apply_restrictions(snp=snp, chr=chromosome, pval_interval=pval_interval, bp_interval=bp_interval)
            result = searcher.get_result()
        return result

    def search_chromosome(self, chromosome, bp_interval=None, study=None, pval_interval=None):
        result = None
        print("Searching for CHROMOSOME!")
        h5file = self.output_path + "/bychr/file_" + str(chromosome) + ".h5"
        if os.path.isfile(h5file):
            searcher = chr_searcher.Search(h5file)
            if bp_interval is not None:
                searcher.query_chr_for_block_range(chromosome, bp_interval)
            else:
                searcher.query_for_chromosome(chromosome)
            searcher.apply_restrictions(study=study, pval_interval=pval_interval)
            result = searcher.get_result()
        return result

    def search_snp(self, snp, study=None, pval_interval=None):
        result = None
        print("Searching for SNP!")
        for chromosome in range(1, 23):
            h5file = self.output_path + "/bysnp/file_" + str(chromosome) + ".h5"
            if os.path.isfile(h5file):
                searcher = snp_searcher.Search(h5file)
                if searcher.snp_in_file(snp):
                    searcher.query_for_snp(snp)
                    searcher.apply_restrictions(study=study, pval_interval=pval_interval)
                    result = searcher.get_result()

        return result


def main():

    args = argument_parser()

    trait, study, chromosome, bp_interval, snp, pval_interval = au.convert_search_args(args)
    path = args.path

    search = Search(path)

    result = None

    if trait is not None:
        if study is not None:
            result = search.search_study(trait, study, snp, chromosome, pval_interval, bp_interval)
        else:
            result = search.search_trait(trait, snp, chromosome, pval_interval, bp_interval)

    elif chromosome is not None:
        result = search.search_chromosome(chromosome, bp_interval, study, pval_interval)

    elif snp is not None:
        result = search.search_snp(snp, study, pval_interval)
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
    parser.add_argument('-trait', help='The trait I am looking for')
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-snp', help='The SNP I am looking for')
    parser.add_argument('-chr', help='The chromosome I am looking for')
    parser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')
    parser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')

    return parser.parse_args()