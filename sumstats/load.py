import argparse
import sys
import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import sumstats.snp.loader as snp_loader
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import filesystem_utils as fsutils


def main():
    args = argument_parser(sys.argv[1:])  # pragma: no cover

    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    loader_type = args.loader
    tsv = args.tsv
    study_meta = args.study_meta
    trait_meta = args.trait_meta
    trait = args.trait
    study = args.study
    chromosome = args.chr
    bp = args.bp
    trait_dir = properties.trait_dir
    snp_dir = properties.snp_dir
    chr_dir = properties.chr_dir

    to_load = fsutils.get_file_path(path=tsvfiles_path, file=tsv)

    study_meta_file = None
    trait_meta_file = None
    if study_meta:
        study_meta_file = fsutils.get_file_path(path=tsvfiles_path, file=study_meta)
    if trait_meta:
        trait_meta_file = fsutils.get_file_path(path=tsvfiles_path, file=trait_meta)

    if loader_type == "trait":
        if trait is None: raise ValueError("You have chosen the trait loader but haven't specified a trait")
        file_name = trait[-2:]

        to_store = fsutils.create_h5file_path(path=h5files_path, file_name=file_name, dir_name=trait_dir)
        loader = trait_loader.Loader(tsv=to_load, h5file=to_store, study=study, trait=trait, study_meta_file=study_meta_file, trait_meta_file=trait_meta_file)
        loader.load()
        loader.close_file()
        print("Load complete!")

    if loader_type == "chr":
        if chromosome is None: raise ValueError(
            "You have chosen the chromosome loader but haven't specified a chromosome")

        to_store = fsutils.create_h5file_path(path=h5files_path, dir_name=chr_dir, file_name=str(chromosome))
        loader = chr_loader.Loader(to_load, to_store, study)
        loader.load()
        loader.close_file()
        print("Load complete!")

    if loader_type == "snp":
        if chromosome is None: raise ValueError(
            "You have chosen the variant loader, you need to specify the chromosome that the variant belongs to")
        if bp is None: raise ValueError(
            "You have chosen the variant loader, you need to specify the upper bp limit that the variant belongs to")

        to_store = fsutils.create_h5file_path(path=h5files_path, dir_name=snp_dir + "/" + str(chromosome), file_name=str(bp))
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
    parser.add_argument('-study_meta', help='The name of the file with study specific metadata', required=False)  # pragma: no cover
    parser.add_argument('-trait_meta', help='The name of the file with trait specific metadata', required=False)  # pragma: no cover

    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover
