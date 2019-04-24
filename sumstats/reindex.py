import argparse
import pandas as pd
from sumstats.common_constants import *


class H5Indexer():
    def __init__(self, h5file):
        self.h5file = h5file

    def reindex_file(self):
        with pd.HDFStore(self.h5file) as store:
            group = store.keys()[0]
            self.create_index(TO_INDEX, group)
            self.create_cs_index(BP_DSET, group)


    def create_index(self, fields, group):
        with pd.HDFStore(self.h5file) as store:
            store.create_table_index(group, columns=fields, optlevel=6, kind='medium')


    def create_cs_index(self, fields, group):
        with pd.HDFStore(self.h5file) as store:
            store.create_table_index(group, columns=fields, optlevel=9, kind='full')


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the HDF5 file to be processed', required=True)
    args = argparser.parse_args()
    
    file = args.f

    indexer = H5Indexer(file)
    indexer.reindex_file()
    

if __name__ == "__main__":
    main()
