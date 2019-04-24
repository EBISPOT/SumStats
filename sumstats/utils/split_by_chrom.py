import argparse
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
import sumstats.load as ld

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-study', help='The study identifier', required=True)
    args = argparser.parse_args()
    
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    chr_dir = properties.chr_dir

    filename = args.f
    study = args.study
    loader = ld.Loader(tsv=filename, tsv_path=tsvfiles_path, chr_dir=chr_dir, study=study)
    loader.split_csv_into_chroms()


if __name__ == "__main__":
    main()
