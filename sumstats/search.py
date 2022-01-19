import argparse
import json
from elasticsearch import Elasticsearch



class Search:
    def __init__(self, es_host):
        self.es_host = es_host
        self.es = Elasticsearch(self.es_host)

    def search_by_rsid(self, rsid):
        return self.es.search(q=rsid)

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
    argparser.add_argument('-bp', help='Filter with baise pair location threshold: -bp floor:ceil')
    argparser.add_argument('-es_host', help='Elasticsearch host URL', default='http://127.0.0.1:9200/')

    args = argparser.parse_args()
    rsid = args.rsid
    es_host = args.es_host

    searcher = Search(es_host)
    print(json.dumps(searcher.search_by_rsid(rsid)))


if __name__ == "__main__":
    main()