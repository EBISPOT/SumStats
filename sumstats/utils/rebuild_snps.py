import pandas as pd
import tables as tb
import subprocess
import os
import glob
import re
from collections import defaultdict
from sumstats.common_constants import *
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import filesystem_utils as fsutils
import sumstats.utils.sqlite_client as sq 


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
    loaded_files_path = properties.loaded_files_path  # pragma: no cover
    study_dir = properties.study_dir
    snp_dir = properties.snp_dir
    database = properties.sqlite_path

    temp = fsutils.create_h5file_path(path=h5files_path, file_name="temp", dir_name=snp_dir)
    snp_map = fsutils.create_h5file_path(path=h5files_path, file_name="snp_map", dir_name=snp_dir)
    print(study_dir)

    master_sizes = defaultdict(list)
    for f in glob.glob("{}/{}/*.h5".format(h5files_path,study_dir)):
        print(f)
        for key, value in get_file_sizes(f).items():
            master_sizes[key].append(int(value))
    snp_itemsize = sorted(master_sizes["snp_size"])[-1]
    print("snp min itemsize: " + str(snp_itemsize))


    for f in glob.glob("{}/*.tsv".format(loaded_files_path)):
        print(f)
        filename= "temp_" + os.path.basename(f)
        temp = os.path.abspath(os.path.join(os.sep, h5files_path, snp_dir, filename))
        print(temp)
        if not os.path.isfile(temp):
            df = pd.read_csv(f, usecols=[SNP_DSET, CHR_DSET, BP_DSET], chunksize=1000000, sep="\t")
            count=1
            for chunk in df:
                chunk = chunk.join(chunk[SNP_DSET].str.extract(r'(?P<rs>[a-zA-Z]*)(?P<id>[0-9]*)'))
                chunk = chunk[["rs", "id", CHR_DSET, BP_DSET]]
                print(count)
                count+=1
                chunk.to_csv(temp, mode='a', header=False, index=False)
        else:
            print("file exists...skipping")

    # sort the files:
    for f in glob.glob("{}/{}/temp*.tsv".format(h5files_path, snp_dir)):
        outfile = f + ".sorted"
        if not os.path.isfile(outfile):
            subprocess.call(["sort", "-u", "-t", ",", "-k2,2n", f, "-o", outfile])

    merge_outfile = os.path.abspath(os.path.join(os.sep, h5files_path, snp_dir, "merge.csv"))
    sorted_files = glob.glob("{}/{}/*.sorted".format(h5files_path, snp_dir))
    print(sorted_files)
    subprocess.call("sort -m {}/{}/*.sorted | uniq > {}".format(h5files_path, snp_dir, merge_outfile), shell=True)
            
    print("merged file complete")

    snpdf = pd.read_csv(merge_outfile, header=None, names=['prefix', 'snp_id', CHR_DSET, BP_DSET],
            dtype={'prefix':str, 'snp_id': str, CHR_DSET: str, BP_DSET: str},
            chunksize=500000
            )

    sql = sq.sqlClient(database)
    sql.drop_rsid_index()
    for chunk in snpdf:
        chunk = list(chunk.itertuples(index=False, name=None))
        sql.cur.execute('BEGIN TRANSACTION')
        sql.cur.executemany("insert or ignore into snp(prefix, rsid, chr, position) values (?, ?, ?, ?)", chunk)
        sql.cur.execute('COMMIT')
    sql.create_rsid_index()

   
   # with pd.HDFStore(snp_map) as store:
   #     count = 1
   #     for chunk in snpdf:
   #         """store in hdf5 as below"""
   #         print(count)
   #         count+=1
   #         chunk.to_hdf(store, 'snp_map',
   #                     complib='blosc',
   #                     complevel=9,
   #                     format='table',
   #                     mode='w',
   #                     append=True,
   #                     data_columns = ['snp_id'],
   #                     min_itemsize={'snp_id': snp_itemsize,
   #                                   'prefix': 8,
   #                                   CHR_DSET:2,
   #                                   BP_DSET:9}
   #                     )


if __name__ == "__main__":
    main()  # pragma: no cover
