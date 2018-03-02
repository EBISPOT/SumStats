import argparse
from os import listdir
from os.path import isfile, join
import sumstats.utils.utils as utils
import sumstats.trait.search.access.service as trait_searcher


class Explorer:
    def __init__(self, path=None):
        if path is None:
            print("Explorer: setting default location for output files")
            path = "/output"
        self.output_path = path

    def get_list_of_traits(self):
        trait_dir_path = self.output_path + "/bytrait"
        h5files = [f for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
        traits = []
        for h5file in h5files:
            searcher = trait_searcher.Service(trait_dir_path + "/" + h5file)
            traits.extend(searcher.list_traits())
            searcher.close_file()

        return traits

    def get_list_of_studies_for_trait(self, trait):
        h5file = utils.create_file_path(self.output_path, "bytrait", trait)
        searcher = trait_searcher.Service(h5file=h5file)
        studies = searcher.list_studies()
        searcher.close_file()
        return [study.split(":")[1].strip(" ") for study in studies]

    def get_list_of_studies(self):
        trait_dir_path = self.output_path + "/bytrait"
        h5files = [f for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
        studies = []
        for h5file in h5files:
            searcher = trait_searcher.Service(trait_dir_path + "/" + h5file)
            studies.extend(searcher.list_studies())
            searcher.close_file()

        return studies

    def get_info_on_study(self, study_to_find):
        trait_dir_path = self.output_path + "/bytrait"
        h5files = [f for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
        for h5file in h5files:
            searcher = trait_searcher.Service(trait_dir_path + "/" + h5file)
            for study in searcher.list_studies():
                if study_to_find == study.split(":")[1].strip(" "):
                    searcher.close_file()
                    return study
            searcher.close_file()


def main():
    args = argument_parser()  # pragma: no cover
    path = args.path  # pragma: no cover
    explorer = Explorer(path)  # pragma: no cover

    if args.traits:  # pragma: no cover
        traits = explorer.get_list_of_traits()
        for trait in traits:
            print(trait)

    if args.studies:  # pragma: no cover
        studies = explorer.get_list_of_studies()
        for study in studies:
            print(study)

    if args.study is not None:  # pragma: no cover
        study = explorer.get_info_on_study(args.study)
        if study is None:
            print("The study does not exist: ", args.study)
        else:
            print(study)


if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser():
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-traits', action='store_true', help='List all the traits')  # pragma: no cover
    parser.add_argument('-studies', action='store_true', help='List all the studies')  # pragma: no cover
    parser.add_argument('-study', help='Will list \'trait: study\' if it exists')  # pragma: no cover
    parser.add_argument('-path',
                        help='The path to the parent of the \'output\' dir where the h5files are stored')  # pragma: no cover

    return parser.parse_args()  # pragma: no cover
