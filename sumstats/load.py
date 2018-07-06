import argparse
import sys
import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import sumstats.snp.loader as snp_loader
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import dataset_utils


def main():
    args = argument_parser(sys.argv[1:])  # pragma: no cover

    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    loader_type = args.loader
    tsv = args.tsv
    trait = args.trait
    study = args.study
    chromosome = args.chr
    bp = args.bp
    trait_dir = properties.trait_dir
    snp_dir = properties.snp_dir
    chr_dir = properties.chr_dir

    to_load = dataset_utils.get_file_path(path=tsvfiles_path, file=tsv)

    if loader_type == "trait":
        if trait is None: raise ValueError("You have chosen the trait loader but haven't specified a trait")

        to_store = dataset_utils.create_h5file_path(path=h5files_path, file_name=trait, dir_name=trait_dir)
        loader = trait_loader.Loader(to_load, to_store, study, trait)
        loader.load()
        loader.close_file()
        print("Load complete!")

    if loader_type == "chr":
        if chromosome is None: raise ValueError(
            "You have chosen the chromosome loader but haven't specified a chromosome")

        to_store = dataset_utils.create_h5file_path(path=h5files_path, dir_name=chr_dir, file_name=str(chromosome))
        loader = chr_loader.Loader(to_load, to_store, study)
        loader.load()
        loader.close_file()
        print("Load complete!")

    if loader_type == "snp":
        if chromosome is None: raise ValueError(
            "You have chosen the variant loader, you need to specify the chromosome that the variant belongs to")
        if bp is None: raise ValueError(
            "You have chosen the variant loader, you need to specify the upper bp limit that the variant belongs to")

        to_store = dataset_utils.create_h5file_path(path=h5files_path, dir_name=snp_dir + "/" + str(chromosome), file_name=str(bp))
        loader = snp_loader.Loader(to_load, to_store, study)
        loader.load()
        loader.close_file()
        print("Load complete!")


if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-tsv', help='The name of the file to be loaded', required=True)  # pragma: no cover
    parser.add_argument('-study',
                        help='The name of the study the variants of this file are associated with', required=True)  # pragma: no cover
    parser.add_argument('-trait',
                        help='The name of the trait the variants of this file are associated with')  # pragma: no cover
    parser.add_argument('-loader', help='The type of loader: [trait|chr|snp]', required=True)  # pragma: no cover
    parser.add_argument('-chr', help='The chromosome that will be loaded')  # pragma: no cover
    parser.add_argument('-bp', help='Upper limit of base pair location that is loaded (for snp loader)')  # pragma: no cover

    properties_handler.add_properties(argparser=parser, args=args)  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover
