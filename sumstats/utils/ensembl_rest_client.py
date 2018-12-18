import requests
import time

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
            if self.slow_down_if_needed(content.headers):
                content = requests.get(self.server + endpoint, headers=hdrs)
            if content:
                data = content.json()
            else:
                data = 'NA'
            self.req_count += 1

        except requests.exceptions.HTTPError as ehe:
            # check if we are being rate limited by the server
            if self.slow_down_if_needed(ehe.headers):
                self.perform_rest_action(endpoint, hdrs)
        except requests.exceptions.RequestException as e:
                print('Request failed for {0}: Status: {1}\n'.format(
                endpoint, e))

        return data

    @staticmethod
    def slow_down_if_needed(headers):
        if 'Retry-After' in headers:
            retry = headers['Retry-After']
            time.sleep(float(retry)) # pragma: no cover
            return True

    @staticmethod
    def set_json_format(headers):
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


    def resolve_location_with_rest(self, rsid):
        variation_request = self.perform_rest_action(
            '/variation/human/{rsid}?'.format(
            rsid=rsid)
            )
        return self.retrieve_location(variation_request)

    @staticmethod
    def retrieve_location(variation_request):
        if "mappings" in variation_request:
            mappings = variation_request["mappings"]
            if len(mappings) > 0:
                if "location" in mappings[0]:
                    return mappings[0]["location"]
        return False
