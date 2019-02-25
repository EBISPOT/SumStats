import argparse
import sys
from os.path import isfile
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.search.access.trait_service as trait_service
import sumstats.study.search.access.study_service as study_service
import sumstats.chr.search.access.chromosome_service as chrom_service
import sumstats.chr.search.chromosome_search as chr_search
import sumstats.utils.sqlite_client as sql_client
from sumstats.errors.error_classes import *
from sumstats.utils import properties_handler
from sumstats.utils.properties_handler import properties


class Explorer:
    def __init__(self, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.study_dir = self.properties.study_dir
        self.trait_dir = self.properties.trait_dir
        self.sqlite_db = self.properties.sqlite_path



    def get_list_of_studies(self):
        studies = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.study_dir)
        for h5file in h5files:
            service = study_service.StudyService(h5file=h5file)
            studies.extend(service.list_studies())
            service.close_file()
        return sorted(list(set(studies)))


    def get_list_of_tissues(self):
        tissues = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.study_dir)
        for h5file in h5files:
            service = study_service.StudyService(h5file=h5file)
            tissues.extend(service.list_tissues())
            service.close_file()
        return sorted(list(set(tissues)))


    def get_list_of_traits(self):
        traits = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            service = trait_service.TraitService(h5file=h5file)
            traits.extend(service.list_traits())
            service.close_file()
        return sorted(traits)


    def get_list_of_studies_for_trait(self, trait):
        studies = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.study_dir)
        for h5file in h5files:
            service = study_service.StudyService(h5file=h5file)
            found_studies = service.list_studies_for_trait(trait)
            if found_studies:
                studies.extend([found_studies])
            service.close_file()
        return sorted(list(set(studies)))






    def get_list_of_chroms(self):
        chroms = []
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.chr_dir)
        for h5file in h5files:
            service = chrom_service.ChromosomeService(h5file=h5file)
            chroms.extend(service.list_chroms())
            service.close_file()

        return sorted(chroms)


    def get_trait_of_study(self, study_to_find):
        #h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        #for h5file in h5files:
        #    service = study_service.StudyService(h5file=h5file)
        #    for trait_study in service.list_trait_study_pairs():
        #        if study_to_find == trait_study.split(":")[1]:
        #            service.close_file()
        #            return trait_study.split(":")[0]
        #    service.close_file()
        sc = sql_client.sqlClient(self.sqlite_db)
        traits = sc.get_trait_of_study(study_to_find)
        if traits:
            return traits
        else:
            # study not found
            raise NotFoundError("Study " + study_to_find)


    def get_studies_of_tissue(self, tissue_to_find):
        try:
            study_list = []
            h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
            for h5file in h5files:
                service = study_service.StudyService(h5file=h5file)
                for trait_study, tissue in service.list_tissue_study_pairs().items():
                    if tissue_to_find == tissue:
                        study = trait_study.split('/')[-1]
                        study_list.append(study)
                service.close_file()
            return sorted(list(set(study_list)))
        except NotFoundError:
            # tissue not found
            raise NotFoundError("Tissue " + tissue_to_find)


    def has_trait(self, trait):
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.trait_dir)
        for h5file in h5files:
            service = trait_service.TraitService(h5file=h5file)
            if service.has_trait(trait):
                return True
        raise NotFoundError("Trait " + trait)


    def has_chromosome(self, chromosome):
        # raises Not Found Error
        search = chr_search.ChromosomeSearch(chromosome=chromosome, start=0, size=0, config_properties=self.properties)
        if search is not None:
            return True
        raise NotFoundError("Chromosome " + str(chromosome))


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


    if args.tissues:  # pragma: no cover
        tissues = explorer.get_list_of_tissues()
        for tissue in tissues:
            print(tissue)

    if args.tissue is not None:  # pragma: no cover
        studies = explorer.get_studies_of_tissue(args.tissue)
        study_list = [study for study in studies]
        if studies is None:
            print("The tissue does not exist: ", args.tissue)
        else:
            print("Tissue " + args.tissue + " belongs to the following studies: " + ','.join(study_list))

if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-traits', action='store_true', help='List all the traits')  # pragma: no cover
    parser.add_argument('-trait', help='List all the studies for a trait')  # pragma: no cover
    parser.add_argument('-studies', action='store_true', help='List all the studies')  # pragma: no cover
    parser.add_argument('-study', help='Will list \'trait: study\' if it exists')  # pragma: no cover
    parser.add_argument('-tissues', action='store_true', help='List all the tissues')  # pragma: no cover
    parser.add_argument('-tissue', help='Will list \'study: tissue\' if it exists')  # pragma: no cover
    parser.add_argument('-chromosomes', action='store_true', help='Will list all the chromosomes')  # pragma: no cover
    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover
