import requests
import urllib

class HTTPManager:
    def request(self, method, url, endpoint, params, headers, json=None, **options):
        try:
            parsed_url = url + endpoint
            response = requests.Session.request(
                method=method,
                url=parsed_url,
                params=params,
                header=headers,
                json=json,
                timeout=self.timeout,
                **options
            )
            response.raise_for_status() 
        except HTTPError as a:
            raise a

    def get(self, url, endpoint, params=None, headers=None, **options):
        return self.request("GET", url, endpoint, params, headers, **options)

    def post(self, url, endpoint, params=None, headers=None, json=None, **options):
        return self.request("POST", url, endpoint, params, headers, json, **options)

    def put(self, url, endpoint, params=None, headers=None, json=None, **options):
        return self.request("PUT", url, endpoint, params, headers, json, **options)