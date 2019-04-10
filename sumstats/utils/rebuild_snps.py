import pandas as pd
import tables as tb
import glob
import re
from collections import defaultdict
from sumstats.common_constants import *
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import filesystem_utils as fsutils


def get_file_sizes(file):
    with tb.open_file(file, mode = "r") as pytab:
        size_dict = {}
        description = pytab.__repr__()    
        size_dict["numrows"] = re.search(r"Table\(([0-9]*),", description).group(1)
        size_dict["snp_size"] = re.search(r"variant_id.*itemsize=([0-9]*),", description).group(1)
        size_dict["other_size"] = re.search(r"other_allele.*itemsize=([0-9]*),", description).group(1)
        size_dict["hmother_size"] = re.search(r"hm_other_allele.*itemsize=([0-9]*),", description).group(1)
        size_dict["effect_size"] = re.search(r"effect_allele.*itemsize=([0-9]*),", description).group(1)
        size_dict["hmeffect_size"] = re.search(r"hm_effect_allele.*itemsize=([0-9]*),", description).group(1)
        return size_dict


def main():
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    tsvfiles_path = properties.tsvfiles_path  # pragma: no cover
    study_dir = properties.study_dir
    snp_dir = properties.snp_dir

    temp = fsutils.create_h5file_path(path=h5files_path, file_name="temp", dir_name=snp_dir)
    master = fsutils.create_h5file_path(path=h5files_path, file_name="master", dir_name=snp_dir)
    print(study_dir)

    master_sizes = defaultdict(list)
    for f in glob.glob("{}/{}/*.h5".format(h5files_path,study_dir)):
        print(f)
        for key, value in get_file_sizes(f).items():
            master_sizes[key].append(int(value))
    snp_itemsize = sorted(master_sizes["snp_size"])[-1]

    for f in glob.glob("{}/{}/*.h5".format(h5files_path,study_dir)):
        print(f)
        with pd.HDFStore(temp) as store:
            df = pd.read_hdf(f, columns=[CHR_DSET,BP_DSET,SNP_DSET], chunksize=1000000, ignore_index=True)
            count=1
            for chunk in df:
                """store in hdf5 as below"""
                print(count)
                count+=1
                chunk.to_hdf(store, 'temp',
                            complib='blosc',
                            complevel=9,
                            format='table',
                            mode='a',
                            min_itemsize={SNP_DSET: snp_itemsize,
                                          CHR_DSET:2,
                                          BP_DSET:9}
                            )
    
        mdf = pd.read_hdf(temp, ignore_index=True)
        mdf.drop_duplicates(inplace=True)
        mdf.sort_values(by=[SNP_DSET], inplace=True)
    
        with pd.HDFStore(master) as mstore:
            mdf.to_hdf(mstore, 'master',
                    complib='blosc',
                    complevel=9,
                    format='table',
                    mode='w',
                    data_columns=[SNP_DSET],
                    min_itemsize={SNP_DSET: snp_itemsize,
                                  CHR_DSET:2,
                                  BP_DSET:9}
                    )


if __name__ == "__main__":
    main()  # pragma: no cover
