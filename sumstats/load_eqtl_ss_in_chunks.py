import argparse
import pandas as pd
from common_constants import *


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-hdf', help='The path to the hdf5 file', required=True)
    argparser.add_argument('-csv', help='The path to the csv OUT file', required=True)
    argparser.add_argument('-trait', help='The trait id, or ids if separated by commas', required=True)
    argparser.add_argument('-study', help='The study identifier', required=True)

    args = argparser.parse_args()

    ss_file = args.f
    hdf_store = args.hdf
    csv_file = args.csv
    study = args.study
    traits = args.trait.split(',')
    traits = pd.DataFrame({'traits':traits}).traits.unique()

    study_group = "/{study}".format(study=study.replace('-','_'))
    
    """ read in the variant column as this will contain the longest values"""
    
    df_part = pd.read_csv(ss_file, sep="\t",
                     dtype=DSET_TYPES,
                     usecols=[EFFECT_DSET, CHR_DSET])
    chromosomes = df_part[CHR_DSET].unique()
    print(chromosomes)

    """set the min_itemsize to the longest for variant, ref and alt"""
    alt_itemsize = df_part[EFFECT_DSET].map(len).max()
    ref_itemsize = alt_itemsize
    
    
    
    
    df = pd.read_csv(ss_file, sep="\t",
                     dtype=DSET_TYPES,
                     usecols=list(TO_LOAD_DSET_HEADERS_DEFAULT), 
                     chunksize=1000000)


    #chromosomes = df.chromosome_ss.unique()
    #traits = df.molecular_trait_id.unique()


    #"""Read in the fields in chunks"""

    #dfss = pd.read_csv(ss_file, sep="\t",
    #                   names=['molecular_trait_id', 'pchr', 'a', 'b',
    #                          'strand', 'c', 'd', 'variant_ss', 'chromosome_ss',
    #                          'position_ss', 'e', 'pvalue', 'beta', 'top'],
    #                   dtype={'chromosome_ss': str, 'position_ss': int, 'variant_ss': str},
    #                   header=None,
    #                   usecols=['molecular_trait_id','variant_ss', 'chromosome_ss',
    #                            'position_ss','pvalue', 'beta'],
    #                   chunksize=1000000)
    #
    #"""Read in the variant and trait files"""
    #dfvar = pd.read_csv(var_file, sep="\t",
    #                    names=['chromosome', 'position', 'variant', 'ref', 'alt',
    #                           'type', 'ac', 'an', 'maf', 'r2'],
    #                    dtype={'chromosome': str, 'position': int, 'variant': str})
    #
    #dftrait = pd.read_csv(phen_file, sep="\t", usecols=['phenotype_id', 'gene_id', 'group_id'])
    #dftrait.columns = ['phenotype_id', 'gene_id', 'molecular_trait_object_id']
    #
    with pd.HDFStore(hdf_store) as store:

        """store in hdf5 as below"""

    #    for chunk in dfss:
    #        merged = pd.merge(chunk, dfvar, how='left', left_on=['variant_ss'], right_on=['variant'])
    #        print("merged one ")
    #        merged2 = pd.merge(merged, dftrait, how='left', left_on=['molecular_trait_id'], right_on=['phenotype_id'])
    #        print("merged two")
    #        
        for chunk in df:
            chunk.dropna(subset=[CHR_DSET, PVAL_DSET, SNP_DSET, EFFECT_DSET, OTHER_DSET])
            chunk.to_hdf(store, study_group,
                        complib='blosc:snappy',
                        format='table',
                        append=True,
                        data_columns=list(TO_INDEX),
                        min_itemsize={OTHER_DSET: ref_itemsize,
                                      EFFECT_DSET: alt_itemsize,
                                      CHR_DSET:2,
                                      BP_DSET:9})

        """Store study specific metadata"""
        store.get_storer(study_group).attrs.study_metadata = {'study': study,
                                                              'chromosomes': chromosomes,
                                                              'traits':traits}




if __name__ == "__main__":
    main()
