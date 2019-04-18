import pandas as pd
import re
import glob
import os
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
from sumstats.chr.constants import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler
from sumstats.utils.interval import *
import sumstats.utils.sqlite_client as sq
from multiprocessing import Pool
from itertools import repeat

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
        self.database = self.properties.sqlite_path
        self.snp_map = fsutils.create_h5file_path(self.search_path, self.properties.snp_dir, "snp_map")

        self.datasets = None #utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = self.search_traversed = 0
        self.df = pd.DataFrame()
        self.condition = self._construct_conditional_statement()
        print(self.condition)


    def _chr_bp_from_snp(self):
        if self._snp_format() is 'rs':
            chromosome, bp_interval = self.map_snp_to_location()
            if chromosome and bp_interval:
                self.chromosome = chromosome
                self.bp_interval = IntInterval().set_string_tuple(bp_interval)
        elif self._snp_format() is 'chr_bp':
            pass

    def map_snp_to_location(self):
        try:
            snp_no_prefix = re.search(r"[a-zA-Z]+([0-9]+)", self.snp).group(1)
            sql = sq.sqlClient(self.database)
            chromosome, position = sql.get_chr_pos(snp_no_prefix)[0]
            bp_interval = ':'.join([str(position), str(position)])
            return (chromosome, bp_interval)
        except AttributeError:
            return (None, None)


    def _snp_format(self):
        prefix = ["rs", "ss"]
        if re.search(r"[a-zA-Z]+[0-9]+", self.snp):
            return "rs"
        elif re.search(r".+_[0-9]+_[ACTGN]+_[ACTGN]+", self.snp):
            return "chr_bp"
        else:
            return False


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

        if self.chromosome:
            #hdfs = fsutils.get_h5files_in_dir(self.search_path, self.study_dir + "/" + str(self.chromosome))
            hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/" + str(self.chromosome) + "/*.h5")
        else:
            hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/[1-25]/*.h5")

        print(hdfs)

        ## This iterates through files one chunksize at a time.
        ## The index tells it which chunk to take from each file.
    
        if self.snp:
            print("checking files for snps")
            pool = Pool(16)
            results = pool.starmap(search_hdf_with_condition, zip(hdfs, repeat(self.snp), repeat(self.condition)))
            pool.close()
            pool.join()
            hdfs = [hdf for hdf in results if hdf is not None]
        

        for hdf in hdfs:
            with pd.HDFStore(hdf, mode='r') as store:
                #key = self._get_group_key(store)
                key = store.keys()[0]
                study = self._get_study_metadata(store, key)['study']
                traits = self._get_study_metadata(store, key)['traits'].tolist()
                #tissue = self._get_study_metadata(store, key)['tissue']

                if self.study and self.study != study:
                    # move on to next study if this isn't the one we want
                    continue

                if self.tissue and self.tissue != tissue:
                    # move on to next tissue if this isn't the one we want
                    continue

                if self.condition:
                    print(self.condition)
                    chunks = store.select(key, chunksize=1, start=self.start, where=self.condition) #set pvalue and other conditions
                else:
                    print("No condition")
                    chunks = store.select(key, chunksize=1, start=self.start)

                chunk_size = chunks.coordinates.size
                n = chunk_size - (self.start + 1)

                # update the number of available results if searching for snp and the snp doesn't match
                #if self.snp:
                #    for chunk in chunks:
                #        if chunk[SNP_DSET].values != self.snp:
                #            n -= 1

                # skip this file if the start is beyond the chunksize
                if n < 0:
                    self.start -= chunk_size
                    continue


                for i, chunk in enumerate(chunks):
                    if self.snp and chunk[SNP_DSET].values != self.snp:
                        pass
                    else:
                        chunk[STUDY_DSET] = study
                        chunk[TRAIT_DSET] = str(traits) 
                        #chunk[TISSUE_DSET] = tissue
                        self.df = pd.concat([self.df, chunk])

                    if len(self.df.index) >= self.size: # break once we have enough
                        break

                    if i == n: # Need to explicitly break loop once complete - not sure why - investigate this
                        self.start = 0
                        break

                if len(self.df.index) >= self.size:
                    self.index_marker += len(self.df.index)
                    break


        self.datasets = self.df.to_dict(orient='list') if len(self.df.index) > 0 else self.datasets # return as lists - but could be parameterised to return in a specified format
        self.index_marker = self.starting_point + len(self.df.index)
        return self.datasets, self.index_marker


        

    def _construct_conditional_statement(self):
        conditions = []
        statement = None

        if self.pval_interval:
            if self.pval_interval.lower_limit:
                conditions.append("{pval} >= {lower}".format(pval = PVAL_DSET, lower = str(self.pval_interval.lower_limit)))
            if self.pval_interval.upper_limit:
                conditions.append("{pval} <= {upper}".format(pval = PVAL_DSET, upper = str(self.pval_interval.upper_limit)))

        #if self.trait:
        #    conditions.append("{trait} == {id}".format(trait=PHEN_DSET, id=str(self.trait)))

        if self.bp_interval:
            if self.bp_interval.lower_limit:
                conditions.append("{bp} >= {lower}".format(bp = BP_DSET, lower = self.bp_interval.lower_limit))
            if self.bp_interval.upper_limit:
                conditions.append("{bp} <= {upper}".format(bp = BP_DSET, upper = self.bp_interval.upper_limit))

        if self.snp:
            self._chr_bp_from_snp()
            if self.bp_interval:
                conditions.append("{bp} >= {lower}".format(bp = BP_DSET, lower = self.bp_interval.lower_limit))
            if self.bp_interval:
                conditions.append("{bp} <= {upper}".format(bp = BP_DSET, upper = self.bp_interval.upper_limit))
            #conditions.append("{snp} == {id}".format(snp=SNP_DSET, id=str(self.snp)))

        if len(conditions) > 0:
            statement = " & ".join(conditions)
        return statement


    def _get_study_metadata(self, store, key):
        return store.get_storer(key).attrs.study_metadata

    def _get_group_key(self, store):
        for (path, subgroups, subkeys) in store.walk():
            for subkey in subkeys:
                return '/'.join([path, subkey])


def search_hdf_with_condition(hdf, snp, condition):
    #hdf, snp, condition = args
    with pd.HDFStore(hdf, mode='r') as store:
        key = store.keys()[0]
        results = store.select(key, where=condition) #set pvalue and other conditions
        if len(results.index) > 0:
            return hdf
        return None
            
