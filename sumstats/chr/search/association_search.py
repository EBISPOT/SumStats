import pandas as pd

import sumstats.explorer as ex
from sumstats.trait.search.access import trait_service
import sumstats.trait.search.trait_search as ts
from sumstats.chr.search.access import chromosome_service
import sumstats.chr.search.chromosome_search as cs
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
from sumstats.chr.constants import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class AssociationSearch:
    def __init__(self, start, size, pval_interval=None, config_properties=None, study=None, chromosome=None,
                 bp_interval=None, trait=None, gene=None, tissue=None, snp=None):
        self.starting_point = start
        self.start = start
        self.size = size
        self.study = study
        self.pval_interval = pval_interval
        self.chromosome = chromosome
        self.bp_interval = bp_interval
        self.trait = trait
        self.gene = gene
        self.tissue = tissue
        self.snp = snp

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.study_dir = self.properties.study_dir

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = self.search_traversed = 0

    def search_associations(self):
        """
        Traverses the hdfs breaking if once the required results are retrieved, while
        keeping track of where it got to for the next search. Chunksize is set to 1 so that
        we can actually do this. If a very large size is requested, it is possible that this
        will be suboptimal for resources i.e. time and memory.
        :return: a dictionary containing the dataset names and slices of the datasets and
        the index marker.
        """
        logger.info("Searching all associations for start %s, size %s, pval_interval %s",
                    str(self.start), str(self.size), str(self.pval_interval))
        self.iteration_size = self.size

        hdfs = fsutils.get_h5files_in_dir(self.search_path, self.study_dir)

        df = pd.DataFrame()
        condition = self._construct_conditional_statement()

        ## This iterates through files one chunksize at a time.
        ## The index tells it which chunk to take from each file.

        for hdf in hdfs:
            with pd.HDFStore(hdf) as store:
                key = None
                for (path, subgroups, subkeys) in store.walk():
                    for subkey in subkeys:
                        key = '/'.join([path, subkey])
                #study = key.split('/')[-1] # set study here

                study = store.get_storer(key).attrs.study_metadata['study']
                tissue = store.get_storer(key).attrs.study_metadata['tissue']

                if self.study and self.study != study:
                    continue

                if self.tissue and self.tissue != tissue:
                    continue

                if condition:
                    print(condition)
                    chunks = store.select(key, chunksize=1, start=self.start, where=condition) #set pvalue and other conditions
                else:
                    chunks = store.select(key, chunksize=1, start=self.start)

                n = chunks.coordinates.size - (self.start + 1)
                # skip this file if the start is beyond the chunksize
                if n < 0:
                    self.start -= chunks.coordinates.size
                    continue

                for i, chunk in enumerate(chunks):
                    chunk[STUDY_DSET] = study
                    chunk[TISSUE_DSET] = tissue
                    df = pd.concat([df, chunk])
                    if len(df.index) >= self.size:
                        break
                    if i == n:
                        self.start = 0
                        break

                if len(df.index) >= self.size:
                    self.index_marker += len(df.index)
                    break


        self.datasets = df.to_dict(orient='list')
        self.index_marker = self.starting_point + len(df.index)
        return self.datasets, self.index_marker


    def _construct_conditional_statement(self):
        conditions = []
        statement = None

        if self.pval_interval:
            if self.pval_interval.lower_limit:
                conditions.append("{pval} >= {lower}".format(pval = PVAL_DSET, lower = str(self.pval_interval.lower_limit)))
            if self.pval_interval.upper_limit:
                conditions.append("{pval} <= {upper}".format(pval = PVAL_DSET, upper = str(self.pval_interval.upper_limit)))

        if self.trait:
            conditions.append("{trait} == {id}".format(trait=PHEN_DSET, id=str(self.trait)))

        if self.chromosome:
            conditions.append("{chr} == '{value}'".format(chr=CHR_DSET, value=str(self.chromosome)))

        if self.bp_interval:
            if self.bp_interval.lower_limit:
                conditions.append("{bp} >= {lower}".format(bp = BP_DSET, lower = self.bp_interval.lower_limit))
            if self.bp_interval.upper_limit:
                conditions.append("{bp} <= {upper}".format(bp = BP_DSET, upper = self.bp_interval.upper_limit))

        if self.snp:
            conditions.append("{snp} == {id}".format(snp=SNP_DSET, id=str(self.snp)))

        if len(conditions) > 0:
            statement = " & ".join(conditions)
        return statement


    #def _get_all_traits(self):
    #    explorer = ex.Explorer(self.properties)
    #    return explorer.get_list_of_traits()
#
    #def _get_all_chroms(self):
    #    explorer = ex.Explorer(self.properties)
    #    return explorer.get_list_of_chroms()
#
    #def _next_iteration_size(self):
    #    return self.size - len(self.datasets[REFERENCE_DSET])
#
    #def _increase_search_index(self, iteration_size):
    #    self.index_marker += iteration_size
#
    #def _extend_datasets(self, result):
    #    self.datasets = utils.extend_dsets_with_subset(self.datasets, result)
#
    #def _calculate_total_traversal_of_search(self, chrom, current_chrom_index):
    #    self.search_traversed += self._get_traversed_size(retrieved_index=current_chrom_index, chrom=chrom)
#
    #def _search_complete(self):
    #    return len(self.datasets[REFERENCE_DSET]) >= self.size
#
    #def _get_traversed_size(self, retrieved_index, chrom):
    #    if retrieved_index == 0:
    #        h5file = fsutils.create_h5file_path(self.search_path, dir_name=self.chr_dir, file_name=chrom)
    #        service = chromosome_service.ChromosomeService(h5file)
    #        chrom_size = service.get_chromosome_size(chrom)
    #        service.close_file()
    #        return chrom_size
    #    return retrieved_index
#
    #def _next_start_index(self, current_search_index):
    #    if current_search_index == self.search_traversed:
    #        # we have retrieved the trait from start to end
    #        # retrieving next trait from it's beginning
    #        return 0
    #    new_start = self.start - self.search_traversed + current_search_index
    #    if new_start < 0:
    #        return self.start + current_search_index
    #    return new_start