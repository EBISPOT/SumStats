import argparse
import sys
from os.path import isfile
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.study_deleter as trait_deleter
from sumstats.errors.error_classes import *
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties


class Deleter:

    def __init__(self, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.trait_dir = self.properties.trait_dir

    def delete_trait_study_group(self):
        pass



def main():
    args = argument_parser(sys.argv[1:])  # pragma: no cover
    explorer = Explorer(properties)  # pragma: no cover

    if args.traits:  # pragma: no cover
        traits = explorer.get_list_of_traits()
        for trait in traits:
            print(trait)

    if args.studies:  # pragma: no cover
        studies = explorer.get_list_of_studies()
        for study in studies:
            print(study)

    if args.study is not None:  # pragma: no cover
        trait = explorer.get_trait_of_study(args.study)
        if trait is None:
            print("The study does not exist: ", args.study)
        else:
            print(trait + ":" + args.study)

if __name__ == "__main__":
    main()  # pragma: no cover

def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-traits', action='store_true', help='List all the traits')  # pragma: no cover
    parser.add_argument('-studies', action='store_true', help='List all the studies')  # pragma: no cover
    parser.add_argument('-study', help='Will list \'trait: study\' if it exists')  # pragma: no cover
    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover


