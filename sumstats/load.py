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


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-trait', help='The trait id, or ids if separated by commas', required=True)
    argparser.add_argument('-study', help='The study identifier', required=True)
    args = argparser.parse_args()
    
    properties_handler.set_properties()  # pragma: no cover

    filename = args.f
    study = args.study
    traits = args.trait.split(',')

    filename_id = filename.split('.')[0]
    traits = pd.DataFrame({'traits':traits}).traits.unique()
    study_group = "/{study}".format(study=study.replace('-','_'))
    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    study_dir = properties.study_dir
    print(study_dir)

    ss_file = fsutils.get_file_path(path=tsvfiles_path, file=filename)
    
    """ read in the variant column as this will contain the longest values"""
    
    df_part = pd.read_csv(ss_file, sep="\t",
                     dtype=DSET_TYPES,
                     usecols=[SNP_DSET, OTHER_DSET, EFFECT_DSET, CHR_DSET, HM_EFFECT_DSET, HM_OTHER_DSET])
    chromosomes = df_part[CHR_DSET].unique()
    num_rows = len(df_part[CHR_DSET].index)

    """set the min_itemsize to the longest for variant, ref and alt"""
    alt_itemsize = df_part[EFFECT_DSET].astype(str).map(len).max()
    ref_itemsize = df_part[OTHER_DSET].astype(str).map(len).max()
    snp_itemsize = df_part[SNP_DSET].astype(str).map(len).max()
    hmalt_itemsize = df_part[HM_EFFECT_DSET].astype(str).map(len).max()
    hmref_itemsize = df_part[HM_OTHER_DSET].astype(str).map(len).max()


    df = pd.read_csv(ss_file, sep="\t",
                     dtype=DSET_TYPES,
                     converters={RANGE_U_DSET: coerce_zero_and_inf_floats_within_limits,
                     RANGE_L_DSET: coerce_zero_and_inf_floats_within_limits,
                     HM_RANGE_U_DSET: coerce_zero_and_inf_floats_within_limits,
                     HM_RANGE_L_DSET: coerce_zero_and_inf_floats_within_limits,
                     PVAL_DSET: coerce_zero_and_inf_floats_within_limits,
                     SE_DSET: coerce_zero_and_inf_floats_within_limits
                     },
                     usecols=list(TO_LOAD_DSET_HEADERS_DEFAULT), chunksize=1000000)

    headers = list(TO_LOAD_DSET_HEADERS_DEFAULT)
    headers.remove(BP_DSET)
    headers = [BP_DSET] + headers
    
    for chunk in df:
        chunk.dropna(subset=list(REQUIRED))
        chunk = chunk[headers] # set bp to first column
        for chrom, data in chunk.groupby(CHR_DSET):
            path = os.path.join(tsvfiles_path, "chr_{}_{}.csv".format(str(chrom), filename_id))
            with open(path, 'a') as f:
                data.to_csv(f, index=False, header=False)

    for f in glob.glob(os.path.join(tsvfiles_path, "chr_*_{}.csv".format(filename_id))):
        outfile = f + ".sorted"
        subprocess.call(["sort", "-t", ",", "-k1,1n", f, "-o", outfile])
        os.remove(f)


    for f in glob.glob(os.path.join(tsvfiles_path, "chr_*_{}.csv.sorted".format(filename_id))):
        chromosome = f.split('/')[-1].split('_')[1]
        print(chromosome)
        hdf_store = fsutils.create_h5file_path(path=h5files_path, file_name=filename_id, dir_name=study_dir + "/" + chromosome)
    
        chrdf = pd.read_csv(f, names=headers, dtype=DSET_TYPES, chunksize=1000000)
        with pd.HDFStore(hdf_store) as store:
            """store in hdf5 as below"""
            count = 1
            for chunk in chrdf:
                print(count)
                count += 1
                chunk.to_hdf(store, study_group,
                            complib='blosc',
                            complevel=9,
                            format='table',
                            mode='w',
                            append=True,
                            expectedrows=num_rows,
                            data_columns=list(TO_INDEX),
                            min_itemsize={OTHER_DSET: ref_itemsize,
                                          EFFECT_DSET: alt_itemsize,
                                          SNP_DSET: snp_itemsize,
                                          HM_EFFECT_DSET: hmalt_itemsize,
                                          HM_OTHER_DSET: hmref_itemsize,
                                          BP_DSET:9}
                            )
                """Store study specific metadata"""
                store.get_storer(study_group).attrs.study_metadata = {'study': study,
                                                                      'chromosomes': chromosomes,
                                                                      'traits':traits}
    
        with tb.open_file(hdf_store, "a") as hdf:
            bp_col = hdf.root[study].table.cols.base_pair_location
            print(bp_col)
            bp_col.remove_index()
            bp_col.create_csindex()
            print(bp_col)

        os.remove(f)


def coerce_zero_and_inf_floats_within_limits(value):
    if value == 'NA':
        value = 'NaN'
    value = float(value)
    if value == 0.0:
        value = sys.float_info.min
    if value == float('inf'):
        value = sys.float_info.max
    return value


if __name__ == "__main__":
    main()
