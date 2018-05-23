import requests
import sys
import csv
import argparse
import time
from pyliftover import LiftOver

sys_paths = ['sumstats/', '../sumstats/', '../../sumstats/']
sys.path.extend(sys_paths)
from sumstats_formatting import *


ucsc_release = {'28': 'hg10',
                '29': 'hg11',
                '30': 'hg13',
                '31': 'hg14',
                '33': 'hg15',
                '34': 'hg16',
                '35': 'hg17',
                '36': 'hg18',
                '37': 'hg19',
                '38': 'hg38'}


suffixed_release = {'28': 'NCBI28',
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
        hdrs = self.set_json_format(hdrs)
        self.rate_check()
        data = None

        try:
            content = requests.get(self.server + endpoint, headers=hdrs)
            self.slow_down_if_needed(content.headers)
            content = requests.get(self.server + endpoint, headers=hdrs)
            if content:
                data = content.json()
            else:
                data = 'NA'
            self.req_count += 1

        except requests.exceptions.RequestException as e:
            # check if we are being rate limited by the server
            if e.code == 429:
                self.slow_down_if_needed(e.headers)
                self.perform_rest_action(endpoint, hdrs)
            else:
                print('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(
                endpoint, e))

        return data

    def slow_down_if_needed(self, headers):
        if 'Retry-After' in headers:
            retry = headers['Retry-After']
            time.sleep(float(retry))

    def set_json_format(self, headers):
        if headers is None:
            headers = {}
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        return headers

    def rate_check(self):
        # check if we need to rate limit ourselves
        if self.req_count >= self.reqs_per_sec:
            time.sleep(1)
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0

    def map_bp_to_build_with_rest(self, chromosome, bp, build_orig, build_mapped):
        map_build = self.perform_rest_action(
            '/map/human/{orig}/{chromosome}:{bp}:{bp}/{mapped}?'.format(
            chromosome=chromosome, bp=bp, orig=build_orig, mapped=build_mapped)
            )
        return self.retrieve_mapped_item(map_build)

    def retrieve_mapped_item(self, map_build):
        if "mappings" in map_build:
            mappings = map_build["mappings"]
            if len(mappings) > 0:
                if "mapped" in mappings and "start" in mappings["mapped"]:
                    return map_build["mappings"][0]["mapped"]["start"]
        return 'NA'

    def resolve_rsid(self, chromosome, bp):
        rsid_request = self.perform_rest_action(
            '/overlap/region/human/{chromosome}:{bp}:{bp}?feature=variation'.format(
            chromosome=chromosome, bp=bp)
            )

        return self.retrieve_rsid(rsid_request)

    def retrieve_rsid(self, rsid_request):
        if len(rsid_request) > 0 and "id" in rsid_request[0]:
            return rsid_request[0]["id"]
        return 'id:NA'


def isNumber(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


# Map using pyLiftover and if that fails map using Ensembl REST API
def map_bp_to_build_via_liftover(chromosome, bp, build_map):
    if isNumber(bp):
        data = build_map.convert_coordinate('chr' + str(chromosome), bp)
        if len(data) > 0:
            return data[0][1]
    return None


def map_bp_to_build_via_ensembl(chromosome, bp, from_build, to_build):
    client = EnsemblRestClient()
    data = client.map_bp_to_build_with_rest(
        chromosome, bp, suffixed_release.get(from_build), suffixed_release.get(to_build)
    )
    return data


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The name of the file to be processed', required=True)
    argparser.add_argument('-original', help='The build of the file', required=True)
    argparser.add_argument('-mapped', help='The build to map to', required=True)
    args = argparser.parse_args()
    file = args.f
    from_build = args.original
    to_build = args.mapped

    filename = get_filename(file)
    header = None
    is_header = True
    lines = []
    build_map = LiftOver(ucsc_release.get(from_build), ucsc_release.get(to_build))
    client = EnsemblRestClient()

    with open(file) as csv_file:
        csv_reader = get_csv_reader(csv_file)
        for row in csv_reader:
            if is_header:
                header = row
                is_header = False
            else:
                chr_index = header.index(CHR_DSET)
                snp_index = header.index(SNP_DSET)
                bp_index = header.index(BP_DSET)

                chromosome = row[chr_index].replace('23', 'X').replace('24', 'Y')
                bp = int(row[bp_index])

                # do the bp location mapping
                mapped_bp = map_bp_to_build_via_liftover(chromosome=chromosome, bp=bp, build_map=build_map)
                if mapped_bp is None:
                    mapped_bp = map_bp_to_build_via_ensembl(chromosome=chromosome, bp=bp, from_build=from_build, to_build=to_build)
                row[bp_index] = mapped_bp

                # lookup missing rsids
                bp = row[bp_index]
                if 'rs' not in row[snp_index]:
                    row[snp_index] = client.resolve_rsid(chromosome, bp)

                lines.append(row)

    new_filename = 'harmonised_' + filename + '.tsv'
    with open(new_filename, 'w') as result_file:
        writer = csv.writer(result_file, delimiter='\t')
        writer.writerows([header])
        writer.writerows(lines)


if __name__ == "__main__":
    main()
