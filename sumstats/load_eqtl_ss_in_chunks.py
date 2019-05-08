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
    def __init__(self, tsv, tsv_path, chr_dir, study_dir, study=None, trait=None, hdf_path=None, chromosome=None, sqldb=None, loader=None):
        self.tsv = tsv
        self.study = study
        self.traits = trait
        self.chromosome = chromosome
        self.hdf_path = hdf_path
        self.tsv_path = tsv_path
        self.chr_dir = chr_dir
        self.study_dir = study_dir
        self.max_string = 255

        self.filename = self.tsv.split('.')[0]
        self.traits = trait

        self.ss_file = fsutils.get_file_path(path=self.tsv_path + "/{chrom}".format(chrom=self.chromosome), file=self.filename + ".csv") if loader in ['bychr', 'bystudy'] else fsutils.get_file_path(path=self.tsv_path, file=self.tsv)

        self.sqldb = sqldb









header_to_keep = ['molecular_trait_id','pvalue', 'beta', 'chromosome',
                  'position', 'variant', 'ref', 'alt', 'type', 'ac',
                  'an', 'maf', 'r2', 'gene_id','molecular_trait_object_id']


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-csv', help='The path to the csv OUT file', required=True)
    argparser.add_argument('-var', help='The path to the variant/genotype metadata file', required=True)
    argparser.add_argument('-phen', help='The path to the trait/phenotype metadata file', required=True)
    argparser.add_argument('-study', help='The study identifier', required=True)
    argparser.add_argument('-tissue', help='The tissue identifier', required=True)
    argparser.add_argument('-chr', help='The chromosome the data belongs to', required=True)
    argparser.add_argument('-loader', help='The loader: either "bychr" or bystudy"', choices=['bystudy', 'study_info'], default=None, required=True)

    args = argparser.parse_args()
    
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    database = properties.sqlite_path
    chr_dir = properties.chr_dir
    study_dir = properties.study_dir

    ss_file = args.f
    csv_file = args.csv
    var_file = args.var
    phen_file = args.phen
    study = args.study
    tissue = args.tissue
    loader = args.loader
    chromosome = args.chr

    if loader_type == 'bystudy':
        if chromosome is None:
            print("You must specify the '-chr'...exiting")
        else:
            loader = Loader(tsv=ss_file, tsv_path=tsvfiles_path, chr_dir=chr_dir, study_dir=study_dir, study=study, trait=phen_file, hdf_path=h5files_path, chromosome=chromosome, sqldb=database, loader=loader)
            loader = Loader(filename, tsvfiles_path, chr_dir, study_dir, study, traits, h5files_path, chromosome, database, loader_type)
            loader.load_bystudy()
    elif loader_type == "study_info":
        loader = Loader(filename, tsvfiles_path, chr_dir, study_dir, study, traits, h5files_path, chromosome, database, loader_type)
        loader.load_study_info()
    else:
        print("You must specify the '-loader'...exiting")


#    study_group = "/{ecst}".format(ecst=ecst.replace('-','_'))
#
#    """ read in the variant column as this will contain the longest values"""
#    df = pd.read_csv(ss_file, sep="\t",
#                     names=['molecular_trait_id', 'pchr', 'a', 'b',
#                            'strand', 'c', 'd', 'variant_ss', 'chromosome_ss',
#                            'position_ss', 'e', 'pvalue', 'beta', 'top'],
#
#
#    """set the min_itemsize to the longest for variant, ref and alt"""
#    var_itemsize = df.variant_ss.map(len).max()
#    ref_itemsize = var_itemsize
#    alt_itemsize = var_itemsize
#    print(var_itemsize)
#
#    chromosomes = df.chromosome_ss.unique()
#    traits = df.molecular_trait_id.unique()
#
#
#    """Read in the fields in chunks"""
#
#    dfss = pd.read_csv(ss_file, sep="\t",
#                       names=['molecular_trait_id', 'pchr', 'a', 'b',
#                              'strand', 'c', 'd', 'variant_ss', 'chromosome_ss',
#                              'position_ss', 'e', 'pvalue', 'beta', 'top'],
#                       dtype={'chromosome_ss': str, 'position_ss': int, 'variant_ss': str},
#                       header=None,
#                       usecols=['molecular_trait_id','variant_ss', 'chromosome_ss',
#                                'position_ss','pvalue', 'beta'],
#                       chunksize=1000000)
#    
#    """Read in the variant and trait files"""
#    dfvar = pd.read_csv(var_file, sep="\t",
#                        names=['chromosome', 'position', 'variant', 'ref', 'alt',
#                               'type', 'ac', 'an', 'maf', 'r2'],
#                        dtype={'chromosome': str, 'position': int, 'variant': str})
#    
#    dftrait = pd.read_csv(phen_file, sep="\t", usecols=['phenotype_id', 'gene_id', 'group_id'])
#    dftrait.columns = ['phenotype_id', 'gene_id', 'molecular_trait_object_id']
#    
#    with pd.HDFStore(hdf_store) as store:
#        first_pass = True
#
#        """store in hdf5 as below"""
#
#        for chunk in dfss:
#            merged = pd.merge(chunk, dfvar, how='left', left_on=['variant_ss'], right_on=['variant'])
#            print("merged one ")
#            merged2 = pd.merge(merged, dftrait, how='left', left_on=['molecular_trait_id'], right_on=['phenotype_id'])
#            print("merged two")
#            
#            store.append(study_group, merged2[header_to_keep],
#                         complib='blosc:snappy',
#                         format='table',
#                         data_columns=['molecular_trait_id', 'chromosome', 'position', 'pvalue'],
#                         min_itemsize={'variant':var_itemsize,
#                                       'ref': ref_itemsize,
#                                       'alt': alt_itemsize,
#                                       'chromosome':2,
#                                       'position':9})
#
#
#            if first_pass:
#                """Store study specific metadata"""
#                store.get_storer(study_group).attrs.study_metadata = {'study': study,
#                                                                      'tissue': tissue,
#                                                                      'chromosomes': chromosomes,
#                                                                      'trait_file': phen_file,
#                                                                      'traits':traits}
#
#                """Store as csv"""
#                merged2.to_csv(csv_file, compression='gzip', columns=header_to_keep,
#                               index=False, mode='w', sep='\t', encoding='utf-8')
#            else:
#                merged2.to_csv(csv_file, compression='gzip', columns=header_to_keep,
#                               header=False, index=False, mode='a', sep='\t', encoding='utf-8')
#
#            first_pass = False

if __name__ == "__main__":
    main()
