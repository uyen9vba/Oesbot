import urllib

from requests import Session

class HTTPManager:
    def __init__():
        self.session = Session()
        self.timeout = 20

    def request(self, method, url, endpoint, params, headers, json=None, **options):
        try:
            parsed_url = url + endpoint
            response = requests.session.request(
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

        return response

    def get(self, url, endpoint, params=None, headers=None, **options):
        return self.request("GET", url, endpoint, params, headers, **options)

    def post(self, url, endpoint, params=None, headers=None, json=None, **options):
        return self.request("POST", url, endpoint, params, headers, json, **options)

    def put(self, url, endpoint, params=None, headers=None, json=None, **options):
        return self.request("PUT", url, endpoint, params, headers, json, **options)