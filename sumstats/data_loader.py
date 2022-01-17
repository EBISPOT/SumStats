import argparse
import sys
from elasticsearch import Elasticsearch, helpers
from sumstats.common_constants import ES_MAPPINGS, TO_LOAD_DSET_HEADERS_DEFAULT, DSET_TYPES
import pandas as pd
import numpy as np


class DataLoader:
    def __init__(self, sumstats_datafile, es_host, index_name, chunksize=1000000):
        self.sumstats_datafile = sumstats_datafile
        self.es_host = es_host
        self.index_name = index_name.lower()
        self.es = Elasticsearch(hosts=es_host)
        self.sumstats_df = None
        self.chunksize = chunksize

    def create_index(self):
        if self._index_exists():
            sys.exit(1)
        else:
            self.es.indices.create(index=self.index_name,
                                   body=ES_MAPPINGS)

    def delete_index(self):
        if self._index_exists():
            self.es.indices.delete(index=self.index_name)
        else:
            sys.exit(1)

    def _index_exists(self):
        exists = self.es.indices.exists(index=self.index_name)
        if exists:
            print("Index: {} exists".format(self.index_name))
        else:
            print("Index: {} does not exist".format(self.index_name))
        return exists

    @staticmethod
    def _create_action(**kwargs):
        return {k: v for k, v in kwargs.items() if v is not None}

    def _sumstats_df_iterator(self):
        chunks = pd.read_csv(self.sumstats_datafile,
                             sep="\t",
                             dtype=DSET_TYPES,
                             usecols=TO_LOAD_DSET_HEADERS_DEFAULT,
                             index_col=False,
                             chunksize=self.chunksize)
        return chunks

    def df_to_es(self):
        for chunk in self._sumstats_df_iterator():
            columns = chunk.columns.tolist()
            bulk = []
            for i, row in enumerate(chunk.itertuples(name=None, index=False)):
                record = dict(zip(columns, [None if np.all(pd.isna(r)) else r for r in row]))
                action = self._create_action(_type='_doc',
                                             _index=self.index_name,
                                             _source=record)
                bulk.append(action)
            self.write_to_es(bulk)

    def write_to_es(self, bulk):
        helpers.bulk(client=self.es, actions=bulk)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the summary statistics file to be processed', required=True)
    argparser.add_argument('-es_host', help='The host URL for the ES instance', required=True)
    argparser.add_argument('-index', help='The name of the index', required=True)

    args = argparser.parse_args()
    sumstats_datafile = args.f
    es_host = args.es_host
    index_name = args.index

    dl = DataLoader(sumstats_datafile, es_host, index_name)
    dl.create_index()
    dl.df_to_es()


if __name__ == "__main__":
    main()
