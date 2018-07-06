import argparse
import sys
from os.path import isfile
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.search.access.trait_service as trait_searcher
import sumstats.trait.search.access.study_service as study_searcher
from sumstats.errors.error_classes import *
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties


class Explorer:
    def __init__(self, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.trait_dir = self.properties.trait_dir

    def get_list_of_traits(self):
        traits = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            searcher = trait_searcher.TraitService(h5file=h5file)
            traits.extend(searcher.list_traits())
            searcher.close_file()

        return traits

    def get_list_of_studies_for_trait(self, trait):
        h5file = fsutils.create_h5file_path(self.search_path, self.trait_dir, trait)
        if not isfile(h5file):
            raise NotFoundError("Trait " + trait)
        searcher = study_searcher.StudyService(h5file=h5file)
        studies = searcher.list_studies()
        searcher.close_file()
        return studies

    def get_list_of_studies(self):
        studies = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            searcher = study_searcher.StudyService(h5file=h5file)
            studies.extend(searcher.list_studies())
            searcher.close_file()

        return studies

    def get_trait_of_study(self, study_to_find):
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            searcher = study_searcher.StudyService(h5file=h5file)
            for trait_study in searcher.list_trait_study_pairs():
                if study_to_find == trait_study.split(":")[1]:
                    searcher.close_file()
                    return trait_study.split(":")[0]
            searcher.close_file()
        # study not found
        raise NotFoundError("Study " + study_to_find)


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
    properties_handler.add_properties(argparser=parser, args=args)

    return parser.parse_args(args)  # pragma: no cover
