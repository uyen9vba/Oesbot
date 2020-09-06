import urllib

import requests


class HTTPManager:
    session = None
    timeout = None

    def init():
        HTTPManager.session = requests.Session()
        HTTPManager.timeout = 20

    def request(method, url, params=None, headers=None, json=None):
        """
        if isinstance(auth, ClientAuth):
            auth_headers = {"Client-ID": auth.client_id}
        else:
            auth_headers = {}

        if headers is None:
            headers = auth_headers
        else:
            headers = {**headers, **auth_headers}
        """

        try:
            return HTTPManager.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json,
                timeout=HTTPManager.timeout
            )
        except requests.HTTPError as a:
            if (a.response_status_code == 401 and "WWW-Authenticate" in a.response_headers):
                return HTTPManager.request(method, url, params, headers, json)
            elif a.response_status_code == 429:
                rate_limit_reset = datetime.datetime.fromtimestamp(int(a.response_headers["Ratelimit-Reset"]), tz.timezone.utc)
                time_to_wait = rate_limit_reset - datetime.datetime.utcnow()

                time.sleep(math.ceil(time_to_wait.total_seconds()))
                return HTTPManager.request(method, url, params, headers, auth, json)
            else:
                raise a

"""
    def get(self, url, params=None, headers=None, **options):
        return self.request("GET", url, params, headers, json, **options)

    def post(self, url, params=None, headers=None, json=None, **options):
        return self.request("POST", url, params, headers, json, **options)

    def put(self, url, params=None, headers=None, json=None, **options):
        return self.request("PUT", url, params, headers, json, **options)
"""

