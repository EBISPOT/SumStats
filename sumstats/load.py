import sys
import subprocess
import glob
import os
import argparse
import pandas as pd
import tables as tb
from sumstats.common_constants import *
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import filesystem_utils as fsutils
import sumstats.utils.sqlite_client as sq 


class Loader():
    def __init__(self, tsv, tsv_path, chr_dir, study=None, trait=None, hdf_path=None, chromosome=None, sqldb=None):
        self.tsv = tsv
        self.study = study
        self.traits = trait
        self.chromosome = chromosome
        self.hdf_path = hdf_path
        self.tsv_path = tsv_path
        self.chr_dir = chr_dir
        self.max_string = 25

        self.filename = self.tsv.split('.')[0]
        self.traits = trait
        self.ss_file = fsutils.get_file_path(path=self.tsv_path, file=self.tsv)

        self.sqldb = sqldb

    def load(self):
        group = "chr" + self.chromosome
        hdf_store = fsutils.create_h5file_path(path=self.hdf_path, file_name=group, dir_name=self.chr_dir)
        self.csv_to_hdf(hdf_store, group)
        self.load_study_and_trait()


    def split_csv_into_chroms(self):
        df = pd.read_csv(self.ss_file, sep="\t",
                         dtype=DSET_TYPES,
                         usecols=list(TO_LOAD_DSET_HEADERS_DEFAULT), 
                         float_precision='high', 
                         chunksize=1000000)

        # write to chromosome files
        for chunk in df:
            chunk.dropna(subset=list(REQUIRED))
            chunk[STUDY_DSET] = int(self.study.replace(GWAS_CATALOG_STUDY_PREFIX, '')) # need to sort this properly to store accession as int
            for field in [SNP_DSET, EFFECT_DSET, OTHER_DSET, HM_EFFECT_DSET, HM_EFFECT_DSET]:
                self.nullify_if_string_too_long(df=chunk, field=field) 
            for chrom, data in chunk.groupby(CHR_DSET):
                path = os.path.join(self.tsv_path, "chr_{}_{}.csv".format(str(chrom), self.filename))
                with open(path, 'a') as f:
                    data.to_csv(f, index=False, header=True)


    def nullify_if_string_too_long(self, df, field):
        mask = df[field].str.len() <= self.max_string
        df[field].where(mask, 'NA', inplace=True)
        

    def csv_to_hdf(self, hdf, group):
        chrdf = pd.read_csv(self.ss_file, dtype=DSET_TYPES, chunksize=1000000)
        with pd.HDFStore(hdf) as store:
            """store in hdf5 as below"""
            count = 1
            for chunk in chrdf:
                print(count)
                count += 1
                chunk.to_hdf(store, group,
                            complib='blosc',
                            complevel=9,
                            format='table',
                            mode='a',
                            append=True,
                            data_columns=list(TO_INDEX),
                            #expectedrows=num_rows,
                            min_itemsize={OTHER_DSET: self.max_string,
                                          EFFECT_DSET: self.max_string,
                                          SNP_DSET: self.max_string,
                                          HM_EFFECT_DSET: self.max_string,
                                          HM_OTHER_DSET: self.max_string},
                            index = False
                            )


    def load_study_and_trait(self):
        sql = sq.sqlClient(self.sqldb)
        for trait in self.traits:
            data = [self.study, trait]
            sql.cur.execute("insert or ignore into study_trait values (?,?)", data)
        sql.cur.execute('COMMIT')



   # def reindex_files(self):
   #     hdfs = fsutils.get_h5files_in_dir(path=self.hdfs_path, dir_name=self.chr_dir)
   #     for f in hdfs:
   #         with pd.HDFStore(f) as store:
   #             group = store.keys()[0]
   #             self.create_index(f, TO_INDEX, group)
   #             self.create_cs_index(f, BP_DSET, group)


   # def create_index(self, hdf, fields, group):
   #     with pd.HDFStore(hdf) as store:
   #         store.create_table_index(group, columns=fields, optlevel=6, kind='medium')


   # def create_cs_index(self, hdf, fields, group):
   #     with pd.HDFStore(hdf) as store:
   #         store.create_table_index(group, columns=fields, optlevel=9, kind='full')



def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-trait', help='The trait id, or ids if separated by commas', required=True)
    argparser.add_argument('-study', help='The study identifier', required=True)
    argparser.add_argument('-chr', help='The chromosome that the associations belong to', required=True)
    args = argparser.parse_args()
    
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    database = properties.sqlite_path
    chr_dir = properties.chr_dir

    filename = args.f
    study = args.study
    chromosome = args.chr
    traits = args.trait.split(',')
    print(study)


    loader = Loader(filename, tsvfiles_path, chr_dir, study, traits, h5files_path, chromosome, database)
    loader.load()


if __name__ == "__main__":
    main()
