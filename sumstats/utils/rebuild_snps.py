import pandas as pd
import tables as tb
import subprocess
import os
import glob
from sumstats.common_constants import *
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler


def main():
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    loaded_files_path = properties.loaded_files_path  # pragma: no cover
    study_dir = properties.study_dir
    snp_dir = properties.snp_dir
    #database = properties.sqlite_path
    snp_path = properties.snp_path

    #temp = fsutils.create_h5file_path(path=h5files_path, file_name="temp", dir_name=snp_dir)
    #snp_map = fsutils.create_h5file_path(path=h5files_path, file_name="snp_map", dir_name=snp_dir)
    print(study_dir)


    for f in glob.glob("{}/*.tsv".format(loaded_files_path)):
        print(f)
        filename= "temp_" + os.path.basename(f)
        temp = os.path.abspath(os.path.join(h5files_path, snp_dir, filename))
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

    merge_outfile = os.path.abspath(os.path.join(h5files_path, snp_dir, "merge.csv"))
    sorted_files = glob.glob("{}/{}/*.sorted".format(h5files_path, snp_dir))
    print(sorted_files)
    subprocess.call("sort -m {}/{}/*.sorted | uniq > {}".format(h5files_path, snp_dir, merge_outfile), shell=True)
            
    print("merged file complete")

    snpdf = pd.read_csv(merge_outfile, header=None, names=['prefix', SNP_DSET, CHR_DSET, BP_DSET],
            dtype={'prefix':str, SNP_DSET: int, CHR_DSET: str, BP_DSET: int},
            chunksize=500000
            )

    #build hdf5 and index
    for chunk in snpdf:
        chunk.to_hdf(snp_path, key='snp', format='table', append=True, data_columns=list(chunk.columns.values), index=False)
    with tb.open_file(snp_path, "a") as hdf:
        col = hdf.root['snp'].table.cols._f_col(SNP_DSET)
        col.remove_index()
        col.create_csindex()
        col = hdf.root['snp'].table.cols._f_col(CHR_DSET)
        col.create_index(optlevel=6, kind="medium")
        col = hdf.root['snp'].table.cols._f_col(BP_DSET)
        col.create_index(optlevel=6, kind="medium")


    #sql = sq.sqlClient(database)
    #sql.drop_rsid_index()
    #for chunk in snpdf:
    #    chunk = list(chunk.itertuples(index=False, name=None))
    #    sql.cur.execute('BEGIN TRANSACTION')
    #    sql.cur.executemany("insert or ignore into snp(prefix, rsid, chr, position) values (?, ?, ?, ?)", chunk)
    #    sql.cur.execute('COMMIT')
    #sql.create_rsid_index()



if __name__ == "__main__":
    main()  # pragma: no cover
