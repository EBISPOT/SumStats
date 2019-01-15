import argparse
import sys
from os.path import isfile
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.study_deleter as trait_deleter
import sumstats.snp.study_deleter as snp_deleter
import sumstats.chr.study_deleter as chr_deleter
from sumstats.errors.error_classes import *
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties


class Deleter(object):

    def __init__(self, study, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.study = study

    def delete_trait_study_group(self):
        trait_study_deleter = trait_deleter.Deleter(study=self.study, config_properties=self.properties)
        trait_study_deleter.delete_study()

    def delete_snp_study_group(self):
        snp_study_deleter = snp_deleter.Deleter(study=self.study, config_properties=self.properties)
        snp_study_deleter.delete_study()

    def delete_chr_study_group(self):
        chr_study_deleter = chr_deleter.Deleter(study=self.study, config_properties=self.properties)
        chr_study_deleter.delete_study()


def main():
    args = argument_parser(sys.argv[1:])  # pragma: no cover
    study = args.study
    deleter = Deleter(study, properties)  # pragma: no cover

    if study is not None:
        deleter.delete_trait_study_group()
        #deleter.delete_snp_study_group()
        deleter.delete_chr_study_group()

if __name__ == "__main__":
    main()  # pragma: no cover

def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-study', help='The study to be deleted')  # pragma: no cover
    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover


