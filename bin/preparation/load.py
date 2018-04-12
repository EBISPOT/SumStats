# Should be run after having run setup_configuration.py on your local machine for a specific file
# Argument is the name of the file to be loaded


import json
import argparse
import subprocess
from os.path import abspath, dirname, join


def get_properties(config):
    with open(config) as config:
        props = json.load(config)
        return {"h5files_path": props["h5files_path"], "tsvfiles_path": props["tsvfiles_path"],
                "max_bp": props["max_bp"], "bp_step": props["bp_step"], "snp_dir": props["snp_dir"],
                "chr_dir": props["chr_dir"], "trait_dir": props["trait_dir"]}


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-config', help='Full path to properties configuration', required=True)
    argparser.add_argument('-f', help='The full path to the file that is to be loaded', required=True)
    argparser.add_argument('-study', help='Study accession', required=True)
    argparser.add_argument('-trait', help='EFO Trait', required=True)
    args = argparser.parse_args()
    config = args.config
    study = args.study
    trait = args.trait

    file = args.f
    filename = file.split("/")[-1]
    if not str(filename).endswith('.tsv'):
        raise ValueError("File is not tab separated file!")

    where_am_i = dirname(abspath(join(__file__, '../')))

    properties = get_properties(config)

    bp_step = str(properties["bp_step"])
    tsvfiles_path = properties["tsvfiles_path"]

    subprocess.call([where_am_i + "/load.sh", filename, study, trait,
                          bp_step, tsvfiles_path, config])


if __name__ == "__main__":
    main()