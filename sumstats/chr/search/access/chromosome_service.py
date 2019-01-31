"""
    Stored as /CHR/BLOCK/DATA
    Where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'bp' list will hold the baise pair location that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]

    Query for all  the data in a specific chromosome. The chromosome query will start at the first bp block
    for start = 0, or skip bp blocks according to the start/size parameters.
"""

import sumstats.chr.search.access.repository as query
import sumstats.utils.group as gu
import sumstats.utils.restrictions as rst
from sumstats.common_constants import *
from sumstats.errors.error_classes import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class ChromosomeService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)
        self.study = []


    def check_study_is_group(self, group):
        if self.study == group.split('/')[-1]:
            print(group)
            return group

    def query(self, chromosome, start, size, study=None):
        logger.debug("Starting query for chromosome %s, start %s, and size %s", str(chromosome), str(start), str(size))
        chr_group = self.file_group.get_subgroup(chromosome)

        self.study = study
        print(self.study)
        if study and not self.file.visit(self.check_study_is_group):
            raise NotFoundError("Study " + self.study)
            self.datasets = query.create_empty_dataset()

        else:
            all_chr_sub_groups = chr_group.get_all_subgroups()

            # we need to get all the study level subgroups from the bp range subgroups
            all_subgroups = gu.generate_subgroups_from_generator_of_subgroups(all_chr_sub_groups)

            self.datasets = query.load_datasets_from_groups(all_subgroups, start, size, study)
            logger.debug("Query for chromosome %s, start %s, and size %s done...", str(chromosome), str(start), str(size))

    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s",
                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)
        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s done...",
                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))

    def get_result(self):
        return self.datasets

    def get_chromosome_size(self, chromosome):
        chromosome_group = self.file_group.get_subgroup(chromosome)
        all_chr_sub_groups = chromosome_group.get_all_subgroups()
        all_subgroups = gu.generate_subgroups_from_generator_of_subgroups(all_chr_sub_groups)
        #size = sum(sub_group.get_max_group_size() for sub_group in all_subgroups)
        size = chromosome_group.get_attribute("size")
        logger.debug("Chromosome %s group size is %s", str(chromosome), str(size))
        print(size)
        return size

    def list_chroms(self):
        chroms = self.file_group.get_all_subgroups_keys()
        return chroms

    def close_file(self):
        logger.debug("Closing file %s...", self.file.file)
        self.file.close()
