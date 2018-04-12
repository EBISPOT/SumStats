# Input: the file that will be loaded (columns should conform in
# sequence with the templates/headers file)
# Will:
# (a) clean up the file from non-valid variant IDs
# (b) move the clean input file to the <parent>/files/toload directory
# (c) create up to 22 sub files named chr_<x>_<filename>.tsv in the
#       <parent>/files/toload directory each file containing the information
#       for its correspoding chromosome
# (d) create up to $bp_step sub files for each chromosome, split for the bp range
#       named bp_<step_iter>_<filename>.tsv in the <parent>/files/toload directory

import json
import argparse
import os
from shutil import copyfile


def get_properties(config):
    with open(config) as config:
        props = json.load(config)
        return {"h5files_path": props["h5files_path"], "tsvfiles_path": props["tsvfiles_path"],
                "local_h5files_path": props["local_h5files_path"], "local_tsvfiles_path": props["local_tsvfiles_path"],
                "max_bp": props["max_bp"], "bp_step": props["bp_step"], "snp_dir": props["snp_dir"],
                "chr_dir": props["chr_dir"], "trait_dir": props["trait_dir"]}


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-config', help='Full path to properties configuration', required=True)
    argparser.add_argument('-f', help='The full path to the file to be processed', required=True)
    argparser.add_argument('-create', action='store_true',
                           help='When argument provided, the directory format will be created. If not, then it will '
                                'just proceed with processing the file.')
    args = argparser.parse_args()
    config = args.config
    file = args.f
    filename = file.split("/")[-1]

    if not str(filename).endswith('.tsv'):
        raise ValueError("File is not tab separated file!")

    where_am_i = os.path.dirname(os.path.abspath(__file__))

    properties = get_properties(config)
    max_bp = int(properties["max_bp"])
    bp_step = int(properties["bp_step"])
    bp_range = int(max_bp / bp_step)
    local_tsvfiles_path = properties["local_tsvfiles_path"]
    local_h5files_path = properties["local_h5files_path"]
    chr_dir = properties["chr_dir"]
    snp_dir = properties["snp_dir"]
    trait_dir = properties["trait_dir"]

    # create input and output directories if they don't exist
    if args.create:
        print("Creating the directory layout")
        if not os.path.exists(local_tsvfiles_path):
            os.makedirs(local_tsvfiles_path)
        chrdir = os.path.join(local_h5files_path, chr_dir)
        if not os.path.exists(chrdir):
            os.makedirs(chrdir)
        snpdir = os.path.join(local_h5files_path, snp_dir)
        if not os.path.exists(snpdir):
            os.makedirs(snpdir)
        traitdir = os.path.join(local_h5files_path, trait_dir)
        if not os.path.exists(traitdir):
            os.makedirs(traitdir)
        bk_traitdir = os.path.join(local_h5files_path, "bk_" + trait_dir)
        if not os.path.exists(bk_traitdir):
            os.makedirs(bk_traitdir)
        bk_chrdir = os.path.join(local_h5files_path, "bk_" + chr_dir)
        if not os.path.exists(bk_chrdir):
            os.makedirs(bk_chrdir)
        bk_snpdir = os.path.join(local_h5files_path, "bk_" + snp_dir)
        if not os.path.exists(bk_snpdir):
            os.makedirs(bk_snpdir)
        for step in range(1, 23):
            snp_chrdir = os.path.join(local_h5files_path, snp_dir, str(step))
            if not os.path.exists(snp_chrdir):
                os.makedirs(snp_chrdir)

    # $base/bin/utils/clean_input.sh "$file"
    # # move it to the correct location
    # mv $base/"$filename"_clean $to_load_location/"$filename"
    copyfile(file, local_tsvfiles_path + "/" + filename)

    # split up the script into one per chromosome
    for chromosome in range(1, 22):
        command = where_am_i + '/split_by_chromosome.py -f ' + file + ' -chr ' + str(
            chromosome) + ' -path ' + local_tsvfiles_path
        os.system('python ' + command)
        chromosome_file = os.path.join(local_tsvfiles_path, "chr_" + str(chromosome) + "_" + filename)
        if os.path.isfile(chromosome_file):
            previous = 0
            step = 1
            for bp in range(0, max_bp, bp_range):
                command = where_am_i + '/split_bp.py -f ' + chromosome_file + ' -start ' + str(
                    previous) + ' -end ' + str(bp) + ' -accession ' + str(step) + ' -path ' + local_tsvfiles_path
                os.system('python ' + command)
                previous = bp
                step += 1


if __name__ == "__main__":
    main()
