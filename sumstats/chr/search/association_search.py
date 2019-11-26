import pandas as pd
import re
import glob
import itertools
import os
from sumstats.errors.error_classes import *
import sumstats.utils.dataset_utils as utils
import sumstats.utils.filesystem_utils as fsutils
import sumstats.trait.search.access.trait_service as ts
from sumstats.chr.constants import *
import logging
from sumstats.utils import register_logger
from sumstats.utils import properties_handler
from sumstats.utils.interval import *
import sumstats.utils.sqlite_client as sq
from itertools import repeat


logger = logging.getLogger(__name__)
register_logger.register(__name__)


class AssociationSearch:
    def __init__(self, start, size, pval_interval=None, config_properties=None, study=None, chromosome=None,
                 bp_interval=None, trait=None, gene=None, tissue=None, snp=None, quant_method=None, qtl_group=None, paginate=True):
        self.starting_point = start
        self.start = start
        self.max_size = 1000
        self.size = size if int(size) <= self.max_size else self.max_size 
        self.study = study
        self.pval_interval = pval_interval
        self.chromosome = chromosome
        self.bp_interval = bp_interval
        self.trait = trait
        self.gene = gene
        self.tissue = tissue
        self.snp = snp
        self.qtl_group = qtl_group
        self.quant_method = quant_method if quant_method else "ge"
        self.paginate = paginate

        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.study_dir = self.properties.study_dir
        self.chr_dir = self.properties.chr_dir
        self.trait_dir = self.properties.trait_dir
        self.database = self.properties.sqlite_path
        self.snpdb = self.properties.snpdb
        self.trait_file = "phen_meta"
        self.hdfs = []
        

        self.datasets = None #utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        # index marker will be returned along with the datasets
        # it is the number that when added to the 'start' value that we started the query with
        # will pinpoint where the next search needs to continue from
        self.index_marker = self.search_traversed = 0
        self.df = pd.DataFrame()
        self.condition = self._construct_conditional_statement()
        logger.debug(self.condition)
        logger.debug("quant: ".format(self.quant_method))


    def _chr_bp_from_snp(self):
        chromosome = None
        bp_interval = None
        if self._snp_format() is 'rs':
            print('rs')
            chromosome, bp_interval = self.map_snp_to_location()
        elif self._snp_format() is 'chr_bp':
            print('chr_bp_style')
            chromosome, bp_interval = self._chr_bp_from_name(self.snp)
        if chromosome and bp_interval:
            self.chromosome = chromosome
            self.bp_interval = IntInterval().set_string_tuple(bp_interval)
            

    def chrom_for_trait(self):
        h5file = fsutils.create_h5file_path(self.search_path, self.trait_dir, self.trait_file)
        trait_service = ts.TraitService(h5file)
        chroms = trait_service.chrom_from_trait(self.trait)
        if len(chroms) == 1:
            self.chromosome = chroms[0]
        elif len(chroms) > 1:
            logger.debug("more than one chrom for this trait?") # need to handle this error
        else:
            logger.debug("No chrom for this trait?") # need to handle this error

    def chrom_for_gene(self):
        h5file = fsutils.create_h5file_path(self.search_path, self.trait_dir, self.trait_file)
        trait_service = ts.TraitService(h5file)
        chroms = trait_service.chrom_from_gene(self.gene)
        if len(chroms) == 1:
            self.chromosome = chroms[0]
        elif len(chroms) > 1:
            logger.debug("more than one chrom for this gene?") # need to handle this error
        else:
            logger.debug("No chrom for this trait?") # need to handle this error


    def map_snp_to_location(self):
        try:
            snp_no_prefix = re.search(r"[a-zA-Z]+([0-9]+)", self.snp).group(1)
            sql = sq.sqlClient(self.snpdb)
            chromosome, position = sql.get_chr_pos(snp_no_prefix)[0]
            bp_interval = ':'.join([str(position), str(position)])
            return (chromosome, bp_interval)
        except AttributeError:
            return (None, None)


    def _snp_format(self):
        prefix = ["rs", "ss"]
        if re.search(r"rs[0-9]+", self.snp):
            return "rs"
        elif re.search(r".+_[0-9]+_[ACTGN]+_[ACTGN]+", self.snp):
            return "chr_bp"
        else:
            return False

    @staticmethod
    def _chr_bp_from_name(name):
        parts = name.split("_")
        chromosome = parts[0].lower().replace("chr","")
        position = parts[1]
        bp_interval = ':'.join([str(position), str(position)])
        return chromosome, bp_interval

    def _narrow_hdf_pool(self):
        if self.tissue and self.study:
            logger.debug("tissue and study")
            sql = sq.sqlClient(self.database)
            file_ids = []
            resp = sql.get_file_ids_for_study_tissue(self.study, self.tissue, self.quant_method)
            if resp:
                file_ids.extend(resp)
                if not self._narrow_by_chromosome(file_ids):
                    raise NotFoundError("Study :{} with tissue: {} and chr {}".format(self.study, self.tissue, self.chromosome))
            else:
                raise NotFoundError("Study :{} with tissue: {} and quantification method: {}".format(self.study, self.tissue, self.quant_method))

        if self.tissue and not self.study:
            logger.debug("tissue")
            sql = sq.sqlClient(self.database)
            file_ids = []
            resp = sql.get_file_ids_for_tissue(self.tissue, self.quant_method)
            if resp:
                file_ids.extend(resp)
                if not self._narrow_by_chromosome(file_ids):
                    raise NotFoundError("Tissue: {} with chr {}".format(self.tissue, self.chromosome))
            else:
                raise NotFoundError("Tissue: {} with quantification method: {}".format(self.tissue, self.quant_method))

        if self.study and not self.tissue:
            logger.debug("study")
            sql = sq.sqlClient(self.database)
            file_ids = []
            resp = sql.get_file_id_for_study(self.study, self.quant_method)
            if resp:
                file_ids.extend(resp)
                if not self._narrow_by_chromosome(file_ids):
                    raise NotFoundError("Study :{} with chr {}".format(self.study, self.chromosome))
            else:
                raise NotFoundError("Study :{} with quantification method: {}".format(self.study, self.quant_method))
                
        if self.trait:
            logger.debug("phen")
            self.chrom_for_trait()
            self.hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/" + str(self.chromosome) + "/file_*+" + str(self.quant_method) + ".h5")
        if self.gene:
            logger.debug("gene")
            self.chrom_for_gene()
            self.hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/" + str(self.chromosome) + "/file_*+" + str(self.quant_method) + ".h5")
        if self.chromosome and all(v is None for v in [self.study, self.trait, self.gene, self.tissue]):
            logger.debug("bp/chr")
            self.hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/" + str(self.chromosome) + "/file_*+" + str(self.quant_method) + ".h5")
        if all(v is None for v in [self.chromosome, self.study, self.gene, self.trait, self.tissue]):
            logger.debug("all")
            self.hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/*/file_*+" + str(self.quant_method) + ".h5") 

    def _narrow_by_chromosome(self, file_ids):
        if self.chromosome:
            logger.debug("chr{}".format(self.chromosome))
            self.hdfs = [glob.glob(os.path.join(self.search_path, self.study_dir) + "/" + str(self.chromosome) + "/file_" + f + ".h5") for f in file_ids]
            self.hdfs = list(itertools.chain.from_iterable(self.hdfs))
        else:
            logger.debug("nochr")
            self.hdfs = [glob.glob(os.path.join(self.search_path, self.study_dir) + "/*/file_" + f + ".h5") for f in file_ids]
            self.hdfs = list(itertools.chain.from_iterable(self.hdfs))
        if self.hdfs:
            return True
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
        self._narrow_hdf_pool()

        #studies = []
        #if self.trait:
        #    sql = sq.sqlClient(self.database)
        #    studies.extend(sql.get_studies_for_trait(self.trait))

        if len(self.hdfs) == 1 and not self.paginate and self.condition:
            print("unpaginated request")
            self.unpaginated_request()
        elif len(self.hdfs) > 1 and (not self.paginate or self.condition):
            print("cannot make an unpaginated request for this resource - only possible for a study + tissue combined with one or more of the following (gene|variant|molecular_trait|chr+pos|pvalue)")
            self.paginated_request()
        else:
            print("paginated request")
            self.paginated_request()
        
        self.datasets = self.df.to_dict(orient='list') if len(self.df.index) > 0 else self.datasets # return as lists - but could be parameterised to return in a specified format
        self.index_marker = self.starting_point + len(self.df.index)
        return self.datasets, self.index_marker


    def paginated_request(self):
        for hdf in self.hdfs:
            with pd.HDFStore(hdf, mode='r') as store:
                print('opened {}'.format(hdf))
                key = store.keys()[0]
                identifier = key.strip("/")
                logger.debug(key)
                study = self._get_study_metadata(identifier)['study']
                tissue = self._get_study_metadata(identifier)['tissue_ont']
                
                if self.study:
                    study = self._get_study_metadata(identifier)['study']
                    if self.study != study:
                        # move on to next study if this isn't the one we want
                        continue

                #if self.tissue and self.tissue != tissue:
                #    # move on to next tissue if this isn't the one we want
                #    continue

                if self.condition:
                    print(self.condition)
                    chunks = store.select(key, chunksize=1, start=self.start, where=self.condition) #set pvalue and other conditions
                else:
                    logger.debug("No condition")
                    chunks = store.select(key, chunksize=1, start=self.start)

                chunk_size = chunks.coordinates.size
                n = chunk_size - (self.start + 1)

                # skip this file if the start is beyond the chunksize
                if n < 0:
                    self.start -= chunk_size
                    continue

                for i, chunk in enumerate(chunks):
                    if self.snp: 
                        # filter for correct snp
                        if self._snp_format() == 'rs':
                            chunk = chunk[chunk[RSID_DSET] == self.snp]
                        elif self._snp_format() == 'chr_bp':
                            chunk = chunk[chunk[SNP_DSET] == self.snp]
                    
                    chunk[STUDY_DSET] = study
                    #chunk[TRAIT_DSET] = str(traits) 
                    chunk[TISSUE_DSET] = tissue
                    self.df = pd.concat([self.df, chunk])

                    if len(self.df.index) >= self.size: # break once we have enough
                        break

                    if i == n: # Need to explicitly break loop once complete - not sure why - investigate this
                        self.start = 0
                        break

                if len(self.df.index) >= self.size:
                    break

        
    def unpaginated_request(self):
        hdf = self.hdfs[0]
        with pd.HDFStore(hdf, mode='r') as store:
            print('opened {}'.format(hdf))
            key = store.keys()[0]
            identifier = key.strip("/")
            logger.debug(key)
            study = self._get_study_metadata(identifier)['study']
            tissue = self._get_study_metadata(identifier)['tissue_ont']
            
            #if self.study:
            #    study = self._get_study_metadata(identifier)['study']
            #    if self.study != study:
            #        # move on to next study if this isn't the one we want
            #        continue

            #if self.tissue and self.tissue != tissue:
            #    # move on to next tissue if this isn't the one we want
            #    continue

            print(self.condition)
            chunk = store.select(key, where=self.condition) #set pvalue and other conditions

            if self.snp: 
                # filter for correct snp
                if self._snp_format() == 'rs':
                    chunk = chunk[chunk[RSID_DSET] == self.snp]
                elif self._snp_format() == 'chr_bp':
                    chunk = chunk[chunk[SNP_DSET] == self.snp]
                
            chunk[STUDY_DSET] = study
            #chunk[TRAIT_DSET] = str(traits) 
            chunk[TISSUE_DSET] = tissue
            self.df = pd.concat([self.df, chunk])


    def _construct_conditional_statement(self):
        conditions = []
        statement = None

        if self.trait:
            self.chrom_for_trait()
            conditions.append("{trait} == {id}".format(trait=PHEN_DSET, id=str(self.trait)))

        if self.gene:
            self.chrom_for_gene()
            conditions.append("{gene} == {id}".format(gene=GENE_DSET, id=str(self.gene)))

        if self.bp_interval:
            if self.bp_interval.lower_limit:
                conditions.append("{bp} >= {lower}".format(bp = BP_DSET, lower = self.bp_interval.lower_limit))
            if self.bp_interval.upper_limit:
                conditions.append("{bp} <= {upper}".format(bp = BP_DSET, upper = self.bp_interval.upper_limit))

        if self.snp:
            self._chr_bp_from_snp()
            print(self.bp_interval.lower_limit)
            if self.bp_interval:
                conditions.append("{bp} >= {lower}".format(bp = BP_DSET, lower = self.bp_interval.lower_limit))
                conditions.append("{bp} <= {upper}".format(bp = BP_DSET, upper = self.bp_interval.upper_limit))

        if self.pval_interval:
            if self.pval_interval.lower_limit:
                conditions.append("{pval} >= {lower}".format(pval = PVAL_DSET, lower = str(self.pval_interval.lower_limit)))
            if self.pval_interval.upper_limit:
                conditions.append("{pval} <= {upper}".format(pval = PVAL_DSET, upper = str(self.pval_interval.upper_limit)))



        #if self.study:
        #    study_id = int(self.study.replace(GWAS_CATALOG_STUDY_PREFIX, ""))
        #    conditions.append("{study} == {query}".format(study=STUDY_DSET, query=study_id))

        if len(conditions) > 0:
            statement = " & ".join(conditions)
        return statement


    def _get_study_metadata(self, key):
        sql = sq.sqlClient(self.database)
        metadata_dict = sql.get_study_context_meta(key)
        return metadata_dict
        #return store.get_storer(key).attrs.study_metadata

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
            
