import sys
import os
import argparse
import pandas as pd
from sumstats.common_constants import *
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import filesystem_utils as fsutils
import sumstats.utils.meta_client as mc
import pathlib


class Loader():
    def __init__(self, tsv, tsv_path, chr_dir, study_dir, snp_dir, study=None, trait=None, hdf_path=None, chromosome=None, sqldb=None, loader=None, metafile=None):
        self.tsv = tsv
        self.study = study
        self.traits = trait
        self.chromosome = chromosome
        self.hdf_path = hdf_path
        self.tsv_path = tsv_path
        self.chr_dir = chr_dir
        self.study_dir = study_dir
        self.snp_dir = snp_dir
        self.max_string = 255

        self.filename = self.tsv.split('.')[0]
        self.traits = trait

        self.ss_file = fsutils.get_file_path(path=self.tsv_path + "/{chrom}".format(chrom=self.chromosome), file=self.filename + ".csv") if loader in ['bychr', 'bystudy'] else fsutils.get_file_path(path=self.tsv_path, file=self.tsv)

        self.sqldb = sqldb
        self.metafile = metafile

    def load_bychr(self):
        group = "chr" + self.chromosome
        hdf_store = fsutils.create_h5file_path(path=self.hdf_path, file_name=group, dir_name=self.chr_dir)
        self.make_output_dirs()
        self.append_csv_to_hdf(hdf_store, group)


    def load_bystudy(self):
        print(self.ss_file)
        group = "/{study}".format(study=self.study.replace('-','_'))
        hdf_store = fsutils.create_h5file_path(path=self.hdf_path, file_name=self.filename, dir_name=self.study_dir + "/" + self.chromosome)
        self.make_output_dirs()
        self.write_csv_to_hdf(hdf_store, group)

    
    def split_csv_into_chroms(self):
        df = pd.read_csv(self.ss_file, sep="\t",
                         dtype=DSET_TYPES,
                         usecols=list(TO_LOAD_DSET_HEADERS_DEFAULT), 
                         converters={RANGE_U_DSET: self.coerce_floats,
                                     RANGE_L_DSET: self.coerce_floats,
                                     PVAL_DSET: self.coerce_floats,
                                     OR_DSET: self.coerce_floats,
                                     BETA_DSET: self.coerce_floats,
                                     SE_DSET: self.coerce_floats,
                                     FREQ_DSET: self.coerce_floats,
                                     HM_OR_DSET: self.coerce_floats,
                                     HM_RANGE_L_DSET: self.coerce_floats,
                                     HM_RANGE_U_DSET: self.coerce_floats,
                                     HM_BETA_DSET: self.coerce_floats,
                                     HM_FREQ_DSET: self.coerce_floats},
                         float_precision='high', 
                         chunksize=1000000)

        # write to chromosome files
        for chunk in df:
            chunk.dropna(subset=list(REQUIRED))
            chunk[STUDY_DSET] = int(self.study.replace(GWAS_CATALOG_STUDY_PREFIX, '')) # need to sort this properly to store accession as int
            for field in [SNP_DSET, EFFECT_DSET, OTHER_DSET, HM_EFFECT_DSET, HM_OTHER_DSET]:
                self.nullify_if_string_too_long(df=chunk, field=field) 
            for chrom, data in chunk.groupby(CHR_DSET):
                path = os.path.join(self.tsv_path, str(chrom), self.filename + ".csv")
                if not os.path.isfile(path):
                    data.to_csv(path, mode='w', index=False, header=True)
                else:
                    data.to_csv(path, mode='a', index=False, header=False)


    def nullify_if_string_too_long(self, df, field):
        mask = df[field].str.len() <= self.max_string
        df[field].where(mask, 'NA', inplace=True)
        

    def append_csv_to_hdf(self, hdf, group):
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


    def write_csv_to_hdf(self, hdf, group):
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
                            mode='w',
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

                """Store study specific metadata"""
                store.get_storer(group).attrs.study_metadata = {'study': self.study}

    def load_study_info(self):
        self.load_study_and_trait()
        self.load_study_filename()

    def load_study_and_trait(self):
        meta = mc.metaClient(self.metafile)
        meta.load_study_trait(self.study, self.traits)

    def load_study_filename(self):
        meta = mc.metaClient(self.metafile)
        meta.load_study_filename(self.study, self.filename)


    @staticmethod
    def coerce_floats(value):
        try:
            value = float(value)
            if value == 0.0:
                value = sys.float_info.min
            elif value == float('Inf'):
                value = sys.float_info.max
        except ValueError:
            return float('NaN')
        return value


    def make_output_dirs(self):
        pathlib.Path(os.path.join(self.hdf_path, self.chr_dir)).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(self.hdf_path, self.study_dir)).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(self.hdf_path, self.snp_dir)).mkdir(parents=True, exist_ok=True)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-trait', help='The trait id, or ids if separated by commas', required=True)
    argparser.add_argument('-study', help='The study identifier', required=True)
    argparser.add_argument('-chr', help='The chromosome that the associations belong to', required=False)
    argparser.add_argument('-loader', help='The loader: either "bychr" or bystudy"', choices=['bychr', 'bystudy', 'study_info'], default=None, required=True)
    args = argparser.parse_args()
    
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    database = properties.sqlite_path
    metafile = properties.meta_path
    chr_dir = properties.chr_dir
    study_dir = properties.study_dir
    snp_dir = properties.snp_dir

    filename = args.f
    study = args.study
    chromosome = args.chr
    loader_type = args.loader
    traits = args.trait.split(',')
    print(study)

    if loader_type == 'bychr':
        if chromosome is None:
            print("You must specify the '-chr'...exiting")
        else:    
            loader = Loader(filename, tsvfiles_path, chr_dir, study_dir, snp_dir, study, traits, h5files_path, chromosome, database, loader_type, metafile)
            loader.load_bychr()
    elif loader_type == 'bystudy':
        if chromosome is None:
            print("You must specify the '-chr'...exiting")
        else:
            loader = Loader(filename, tsvfiles_path, chr_dir, study_dir, snp_dir, study, traits, h5files_path, chromosome, database, loader_type, metafile)
            loader.load_bystudy()
    elif loader_type == "study_info":
        loader = Loader(filename, tsvfiles_path, chr_dir, study_dir, snp_dir, study, traits, h5files_path, chromosome, database, loader_type, metafile)
        loader.load_study_info()
    else:
        print("You must specify the '-loader'...exiting")
        

if __name__ == "__main__":
    main()
