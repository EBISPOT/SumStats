import argparse
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

"""
s = Search(using=client, index="my-index") \
    .filter("term", category="search") \
    .query("match", title="python")   \
    .exclude("match", description="beta")
"""

class SumStatsSearch:
    def __init__(self, es_host):
        self.es_host = es_host
        self.es = Elasticsearch(self.es_host)
        self.results = None
        self.results_total = 0

    def search_by_rsid(self, rsid, index=None):
        s = Search(using=self.es).filter("term", hm_rsid=rsid)
        response = s.execute()
        self.process_response(response)

    def process_response(self, response):
        if response.success():
            self.results_total = response.hits.total.value
            self.results = [h.to_dict()['_source'] for h in response.hits.hits]

    def search_by_location(self, chromosome, bp_lower, bp_upper, index=None):
        s = Search(using=self.es).filter("term", hm_chrom=chromosome) \
            .filter("range", hm_pos={'gte': bp_lower, 'lte': bp_upper})
        #s = s[1:2] # can paginate like so
        response = s.execute()
        self.process_response(response)
        #self.es.search(index=index, body=body)



def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-all', action='store_true',
                        help='Use argument if you want to search for all associations')  # pragma: no cover
    argparser.add_argument('-start', help='Index of the first association retrieved')  # pragma: no cover
    argparser.add_argument('-size', help='Number of retrieved associations')  # pragma: no cover
    argparser.add_argument('-trait', help='The trait I am looking for')  # pragma: no cover
    argparser.add_argument('-study', help='The study I am looking for')  # pragma: no cover
    argparser.add_argument('-rsid', help='The rsID to query')  # pragma: no cover
    argparser.add_argument('-chr', help='The chromosome I am looking for')  # pragma: no cover
    argparser.add_argument('-pval', help='Filter by pval threshold: -pval floor:ceil')  # pragma: no cover
    argparser.add_argument('-bp_lower', help='Filter with lower base pair location threshold')
    argparser.add_argument('-bp_upper', help='Filter with upper base pair location threshold')
    argparser.add_argument('-es_host', help='Elasticsearch host URL', default='http://127.0.0.1:9200/')

    args = argparser.parse_args()
    rsid = args.rsid
    chromosome = args.chr
    bp_lower = args.bp_lower
    bp_upper = args.bp_upper
    es_host = args.es_host

    searcher = SumStatsSearch(es_host)

    searcher.search_by_location(chromosome=chromosome, bp_lower=bp_lower, bp_upper=bp_upper)
    #searcher.search_by_rsid(rsid=rsid)
    print("Number of results: {}".format(searcher.results_total))
    print(searcher.results)



if __name__ == "__main__":
    main()