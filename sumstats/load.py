import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import sumstats.snp.loader as snp_loader
import argparse


def main():
    args = argument_parser()

    loader_type = args.loader
    tsv = args.tsv
    trait = args.trait
    study = args.study
    output_path = args.output_path
    input_path = args.input_path
    chromosome = args.chr

    assert tsv is not None, "You need to specify the filename to be loaded"
    assert loader_type is not None, "You need to specify a loader: [trait|chromosome|snp]"

    if output_path is None:
        print("Setting default location for output files")
        output_path = ""

    if input_path is None:
        print("Setting default location for input files")
        input_path = ""

    output_path = output_path + "/output"
    input_path = input_path + "/toload"
    to_load = input_path + "/" + tsv

    if loader_type == "trait":
        assert trait is not None, "You have chosen the trait loader but haven't specified a trait"
        assert study is not None, "You have chosen the trait loader but haven't specified a study association"
        # assert study is not None, "You have chosen the trait loader but haven't specified a trait"
        to_store = output_path + "/bytrait/file_" + trait + ".h5"
        loader = trait_loader.Loader(to_load, to_store, study, trait)
        loader.load()
        print("Load complete!")

    if loader_type == "chr":
        assert chromosome is not None, "You have chosen the chr loader but haven't specified a chromosome"
        assert study is not None, "You have chosen the chr loader but haven't specified a study association"

        to_store = output_path + "/bychr/file_" + str(chromosome) + ".h5"
        loader = chr_loader.Loader(to_load, to_store, study)
        loader.load()
        print("Load complete!")

    if loader_type == "snp":
        assert chromosome is not None, "You have chosen the snp loader, you need to specify the chromosome that the " \
                                       "SNP belongs to!"
        assert study is not None, "You have chosen the snp loader but haven't specified a study association"

        to_store = output_path + "/bysnp/file_" + str(chromosome) + ".h5"
        loader = snp_loader.Loader(to_load, to_store, study)
        loader.load()
        print("Load complete!")


if __name__ == "__main__":
    main()


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help='The name of the file to be loaded')
    parser.add_argument('-study', help='The name of the study the variants of this file are associated with')
    parser.add_argument('-trait', help='The name of the trait the variants of this file are associated with')
    parser.add_argument('-loader', help='The type of loader: [trait|chr|snp]')
    parser.add_argument('-chr', help='The chromosome that will be loaded')
    parser.add_argument('-input_path', help='The path to the parent of the \'toload\' dir where the files to be '
                                            'loaded reside')
    parser.add_argument('-output_path', help='The path to the parent of the \'output\' dir where the h5files will be '
                                             'stored')

    return parser.parse_args()