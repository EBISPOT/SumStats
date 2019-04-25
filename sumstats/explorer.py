import argparse
import os
import sys
from os.path import isfile
import glob
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.search.access.trait_service as trait_service
import sumstats.study.search.access.study_service as study_service
import sumstats.chr.search.access.chromosome_service as chrom_service
import sumstats.chr.search.chromosome_search as chr_search
import sumstats.utils.sqlite_client as sql_client
import sumstats.chr.retriever as cr
from sumstats.errors.error_classes import *
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties
from sumstats.common_constants import *


class Explorer:
    def __init__(self, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.study_dir = self.properties.study_dir
        self.chr_dir = self.properties.chr_dir
        self.trait_dir = self.properties.trait_dir
        self.sqlite_db = self.properties.sqlite_path
        

    def get_list_of_studies(self):
        sq = sql_client.sqlClient(self.sqlite_db)
        studies = sq.get_studies()
        return sorted(list(set(studies)))


    def get_list_of_traits(self): 
        sq = sql_client.sqlClient(self.sqlite_db)
        traits = sq.get_traits()
        return traits


    def get_list_of_studies_for_trait(self, trait): 
        sq = sql_client.sqlClient(self.sqlite_db)
        studies = sq.get_studies_for_trait(trait)
        if studies:
            return sorted(list(set(studies)))
        else:
            raise NotFoundError("Trait " + trait)


    def get_trait_of_study(self, study_to_find):
        sq = sql_client.sqlClient(self.sqlite_db)
        traits = sq.get_traits_for_study(study_to_find)
        if traits:
            return sorted(list(set(traits)))
        else:
            # study not found
            raise NotFoundError("Study " + study_to_find)


    def has_trait(self, trait):
        search = cr.search_all_assocs(trait=trait, start=0, size=0, properties=self.properties)
        if search[-1] > 0:
            return True
        raise NotFoundError("Trait " + trait)


    def get_list_of_chroms(self):
        #return CHROMOSOMES
        chromosomes = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.chr_dir)
        for h5file in h5files:
            service = chrom_service.ChromosomeService(h5file=h5file)
            chromosomes.append(service.chromosome)
        return sorted(list(set(chromosomes)))


    def has_chromosome(self, chromosome):
        # raises Not Found Error
        """To do: Store the chromosome list as an attribute in the hdf5 file."""
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.study_dir)
        #chromosomes = []
        #for h5file in h5files:
        #    service = trait_service.StudyService(h5file=h5file)
        #    traits.extend(service.list_traits())
        #    service.close_file()
        search = cr.search_all_assocs(chromosome=chromosome, start=0, size=0, properties=self.properties)
        if search[-1] > 0:
            print('checked')
            return True
        raise NotFoundError("Chromosome " + str(chromosome))


def get_study_attr(h5file):
    service = study_service.StudyService(h5file=h5file)
    study = service.study
    service.close_file()
    return study


def get_trait_attr(h5file):
    service = study_service.StudyService(h5file=h5file)
    traits = service.traits
    service.close_file()
    return traits


def main():

    args = argument_parser(sys.argv[1:])  # pragma: no cover
    explorer = Explorer(properties)  # pragma: no cover

    if args.traits:  # pragma: no cover
        traits = explorer.get_list_of_traits()
        for trait in traits:
            print(trait)

    if args.trait is not None:  # pragma: no cover
        studies = explorer.get_list_of_studies_for_trait(args.trait)
        for study in studies:
            print(study)

    if args.chromosomes:  # pragma: no cover
        chroms = explorer.get_list_of_chroms()
        for chrom in chroms:
            print(chrom)

    if args.studies:  # pragma: no cover
        studies = explorer.get_list_of_studies()
        for study in studies:
            print(study)

    if args.study is not None:  # pragma: no cover
        traits = explorer.get_trait_of_study(args.study)
        if traits is None:
            print("The study does not exist: ", args.study)
        else:
            for trait in traits:
                print(trait + ":" + args.study)


if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-traits', action='store_true', help='List all the traits')  # pragma: no cover
    parser.add_argument('-trait', help='List all the studies for a trait')  # pragma: no cover
    parser.add_argument('-studies', action='store_true', help='List all the studies')  # pragma: no cover
    parser.add_argument('-study', help='Will list \'trait: study\' if it exists')  # pragma: no cover
    parser.add_argument('-chromosomes', action='store_true', help='Will list all the chromosomes')  # pragma: no cover
    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover
