import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import sumstats.snp.loader as snp_loader
import argparse
from config import properties
from sumstats.utils import set_properties
from sumstats.utils import utils


def main():
    args = argument_parser()  # pragma: no cover
    if args.config is not None: # pragma: no cover
        set_properties.set_properties(args.config)
    output_path = properties.output_path # pragma: no cov
    input_path = properties.input_path  # pragma: no cov
    loader_type = args.loader
    tsv = args.tsv
    trait = args.trait
    study = args.study
    chromosome = args.chr

    to_load = utils.create_file_path(path=input_path, file=tsv)

    if loader_type == "trait":
        if trait is None: raise ValueError("You have chosen the trait loader but haven't specified a trait")

        to_store = utils.create_h5file_path(path=output_path, file_name=trait, dir_name="bytrait")
        loader = trait_loader.Loader(to_load, to_store, study, trait)
        loader.load()
        loader.close_file()
        print("Load complete!")

    if loader_type == "chr":
        if chromosome is None: raise ValueError(
            "You have chosen the chromosome loader but haven't specified a chromosome")

        to_store = utils.create_h5file_path(path=output_path, dir_name="bychr", file_name=str(chromosome))
        loader = chr_loader.Loader(to_load, to_store, study)
        loader.load()
        loader.close_file()
        print("Load complete!")

    if loader_type == "snp":
        if chromosome is None: raise ValueError(
            "You have chosen the variant loader, you need to specify the chromosome that the variant belongs to")

        to_store = utils.create_h5file_path(path=output_path, dir_name="bysnp", file_name=str(chromosome))
        loader = snp_loader.Loader(to_load, to_store, study)
        loader.load()
        loader.close_file()
        print("Load complete!")


if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser():
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-tsv', help='The name of the file to be loaded', required=True)  # pragma: no cover
    parser.add_argument('-study',
                        help='The name of the study the variants of this file are associated with', required=True)  # pragma: no cover
    parser.add_argument('-trait',
                        help='The name of the trait the variants of this file are associated with')  # pragma: no cover
    parser.add_argument('-loader', help='The type of loader: [trait|chr|snp]', required=True)  # pragma: no cover
    parser.add_argument('-chr', help='The chromosome that will be loaded')  # pragma: no cover
    parser.add_argument('-config', help='The configuration file to use instead of default') # pragme: no cover

    return parser.parse_args()  # pragma: no cover
