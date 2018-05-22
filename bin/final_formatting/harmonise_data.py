import requests
import sys
import csv
import argparse
import json
import time
import sqlite3
from pyliftover import LiftOver

sys_paths = ['sumstats/', '../sumstats/', '../../sumstats/']
sys.path.extend(sys_paths)
from sumstats_formatting import *


ucsc_release = {    '28': 'hg10',
                    '29': 'hg11',
                    '30': 'hg13',
                    '31': 'hg14',
                    '33': 'hg15',
                    '34': 'hg16',
                    '35': 'hg17',
                    '36': 'hg18',
                    '37': 'hg19',
                    '38': 'hg38'}


suffixed_release = {   '28': 'NCBI28',
                       '29': 'NCBI29',
                       '30': 'NCBI30',
                       '31': 'NCBI31',
                       '33': 'NCBI33',
                       '34': 'NCBI34',
                       '35': 'NCBI35',
                       '36': 'NCBI36',
                       '37': 'GRCh37',
                       '38': 'GRCh38'}


class EnsemblRestClient(object):
    def __init__(self, server='http://rest.ensembl.org', reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0

    def perform_rest_action(self, endpoint, hdrs=None):
        if hdrs is None:
            hdrs = {}

        if 'Content-Type' not in hdrs:
            hdrs['Content-Type'] = 'application/json'

        data = None

        # check if we need to rate limit ourselves
        if self.req_count >= self.reqs_per_sec:
            time.sleep(1)
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0

        try:
            content = requests.get(self.server + endpoint, headers=hdrs)
            if 'Retry-After' in content.headers: 
                retry = content.headers['Retry-After']
                time.sleep(float(retry))
                content = requests.get(self.server + endpoint, headers=hdrs) 
            if content:
                data = content.json()
            else:
                data = 'NA'
            self.req_count += 1

        except requests.exceptions.RequestException as e:
            # check if we are being rate limited by the server
            if e.code == 429:
                if 'Retry-After' in e.headers:
                    retry = e.headers['Retry-After']
                    time.sleep(float(retry))
                    self.perform_rest_action(endpoint, hdrs)
            else:
                print('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(
                endpoint, e))

        return data


    def map_bp_to_build_with_rest(self, chromosome, bp, build_orig, build_mapped):
        map_build = self.perform_rest_action(
            '/map/human/{orig}/{chromosome}:{bp}:{bp}/{mapped}?'.format(
            chromosome=chromosome, bp=bp, orig=build_orig, mapped=build_mapped)
            )
        try:
            bp_mapped = map_build["mappings"][0]["mapped"]["start"]
        except IndexError:
            bp_mapped = 'NA'
        return bp_mapped


    def get_rsid(self, chromosome, bp):
        rsid_request = self.perform_rest_action(
            '/overlap/region/human/{chromosome}:{bp}:{bp}?feature=variation'.format(
            chromosome=chromosome, bp=bp)
            )
        try:
            return rsid_request[0]["id"]
        except IndexError: 
            return 'id:NA'


def get_index(header, col):
    return header.index(col)


# Map using pyLiftover and if that fails map using Ensembl REST API
def map_bp_to_build(chromosome, bp, build_map, build_orig, build_mapped):
    try:
        data = build_map.convert_coordinate('chr' + chromosome, bp)[0][1]
    except IndexError:
        client = EnsemblRestClient()
        data = client.map_bp_to_build_with_rest(
            chromosome, bp, suffixed_release.get(build_orig), suffixed_release.get(build_mapped)
            )
    return data


# sqlite database connection
def create_conn(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


# get the rsid from the sqlite database and if that fails get from Ensembl REST API
def select_rsid_on_chr_bp(conn, chromosome, bp):
    cur = conn.cursor()
    cur.execute("SELECT name FROM snp150Common WHERE chromend=? and chrom=?", (bp, 'chr' + chromosome))
    row = cur.fetchone() # do i need to fetchall and check the number of rows?
    if row: 
        return row[0]
    else:
        client = EnsemblRestClient()
        return client.get_rsid(chromosome, bp)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The name of the file to be processed', required=True)
    argparser.add_argument('-original', help='The build of the file', required=True)
    argparser.add_argument('-mapped', help='The build to map to', required=True)
    args = argparser.parse_args()
    file = args.f
    build_orig = args.original
    build_mapped = args.mapped

    filename = get_filename(file)
    header = None
    is_header = True
    lines = []
    build_map = LiftOver(ucsc_release.get(build_orig), ucsc_release.get(build_mapped))
    database = 'snp.sqlite'
    conn = create_conn(database)
    client = EnsemblRestClient()

    with open(file) as csv_file:
        csv_reader = get_csv_reader(csv_file)
        for row in csv_reader:
            if is_header:
                header = row
                is_header = False
            else:
                chr_index = get_index(header, CHR_DSET)
                snp_index = get_index(header, SNP_DSET)
                bp_index = get_index(header, BP_DSET)

                chromosome = row[chr_index].replace('23', 'X').replace('24', 'Y')
                bp = int(row[bp_index])

                # do the bp location mapping
                row[bp_index] = map_bp_to_build(chromosome, bp, build_map, build_orig, build_mapped)

                # lookup missing rsids
                bp = row[bp_index]
                if 'rs' not in row[snp_index]:
                    try:
                        row[snp_index] = (select_rsid_on_chr_bp(conn, chromosome, int(bp)))
                    except ValueError:
                        row[snp_index] = 'id:NA'

                lines.append(row)

    new_filename = 'harmonised_' + filename + '.tsv'
    with open(new_filename, 'w') as result_file:
        writer = csv.writer(result_file, delimiter='\t')
        writer.writerows([header])
        writer.writerows(lines)


if __name__ == "__main__":
    main()
