import argparse
from os import listdir
from os.path import isfile, join
import sumstats.trait.searcher as trait_searcher


def main():
    args = argument_parser()
    path = args.path
    if path is None:
        print("Setting default location for output files")
        path = ""

    output_path = path + "/output"

    if args.traits:
        trait_dir_path = output_path + "/bytrait"
        h5files = [f for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
        traits = []
        for h5file in h5files:
            searcher = trait_searcher.Search(trait_dir_path + "/" + h5file)
            traits.extend(searcher.list_traits())

        for trait in traits:
            print(trait)

    if args.studies:
        trait_dir_path = output_path + "/bytrait"
        h5files = [f for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
        studies = []
        for h5file in h5files:
            searcher = trait_searcher.Search(trait_dir_path + "/" + h5file)
            studies.extend(searcher.list_studies())

        for study in studies:
            print(study)

    if args.study is not None:
        trait_dir_path = output_path + "/bytrait"
        h5files = [f for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
        for h5file in h5files:
            searcher = trait_searcher.Search(trait_dir_path + "/" + h5file)
            for study in searcher.list_studies():
                if args.study == study.split(":")[1].strip(" "):
                    print(study)
                    return

        print("The study does not exist: ", args.study)


if __name__ == "__main__":
    main()


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-traits', action='store_true', help='List all the traits')
    parser.add_argument('-studies', action='store_true', help='List all the studies')
    parser.add_argument('-study', help='Will list \'trait: study\' if it exists')
    parser.add_argument('-path', help='The path to the parent of the \'output\' dir where the h5files are stored')

    return parser.parse_args()