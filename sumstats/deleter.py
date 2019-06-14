import argparse
import sys
from os.path import isfile
import sumstats.utils.filesystem_utils as fsutils
import sumstats.study.study_deleter as study_deleter
import sumstats.chr.study_deleter as chr_deleter
import sumstats.utils.sqlite_client as sq
from sumstats.errors.error_classes import *
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties


class Deleter(object):

    def __init__(self, study, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.database = self.properties.sqlite_path
        self.study = study

    def delete_chr_study_group(self):
        chr_study_deleter = chr_deleter.Deleter(study=self.study, config_properties=self.properties)
        chr_study_deleter.delete_study()

    def delete_study_files(self):
        study_file_deleter = study_deleter.Deleter(study=self.study, config_properties=self.properties)
        study_file_deleter.delete_study_hdfs()

    def delete_study_metadata(self):
        sql = sq.sqlClient(self.database)
        sql.delete_study(self.study)


def main():
    args = argument_parser(sys.argv[1:])  # pragma: no cover
    study = args.study
    deleter = Deleter(study, properties)  # pragma: no cover

    if study is not None:
        print("Removing {} group from chromosome files".format(study))
        deleter.delete_chr_study_group()
        print("Removing {} study files".format(study))
        deleter.delete_study_files()
        print("Removing {} metadata".format(study))
        deleter.delete_study_metadata()


if __name__ == "__main__":
    main()  # pragma: no cover

def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-study', help='The study to be deleted')  # pragma: no cover
    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover


