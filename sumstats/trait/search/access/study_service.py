"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'chr' list will hold the chromosome that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], mantissa[0], exp[0], and chr[0] hold the information for SNP 0

    Query 1: Retrieve all information for trait: input = query number (1) and trait name
    Query 2: Retrieve all the information for a study: input = query number (2) and study name and trait name

    Can filter based on p-value thresholds, bp position thresholds, SNP, CHR
"""

import sumstats.trait.search.access.repository as repo
import sumstats.utils.group as gu
import sumstats.utils.restrictions as rst
from sumstats.common_constants import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class StudyService:
    def __init__(self, h5file):
        # Open the file with read permissions
        self.file = h5py.File(h5file, 'r')
        self.datasets = {}
        self.file_group = gu.Group(self.file)

    def query(self, trait, study, start, size):
        logger.debug("Starting query for trait %s, study %s, start %s, size %s", trait, study, str(start), str(size))
        trait_group = self.file_group.get_subgroup(trait)
        study_group = trait_group.get_subgroup(study)

        self.datasets = repo.get_dsets_from_group_directly(study, study_group, start, size)
        logger.debug("Query for trait %s, study %s, start %s, size %s done...", trait, study, str(start), str(size))

    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s",
                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))
        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)
        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s done...",
                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))

    def get_result(self):
        return self.datasets

    def get_study_size(self, trait, study):
        trait_group = self.file_group.get_subgroup(trait)
        study_size = trait_group.get_subgroup(study).get_dset_shape(REFERENCE_DSET)[0]
        logger.debug("Study %s has group size %s", study, str(study_size))
        return study_size

    def list_trait_study_pairs(self):
        trait_groups = self.file_group.get_all_subgroups()
        study_groups = []

        for trait_group in trait_groups:
            study_groups.extend(trait_group.get_all_subgroups())
        return [study_group.get_name().strip("/").replace("/",":") for study_group in study_groups]

    def close_file(self):
        logger.debug("Closing file %s...", self.file.file)
        self.file.close()
