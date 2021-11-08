from toolbox import log, pp
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from json import dumps

# TODO: FINISH


def silence_request_warnings() -> None:
    """Silence warning for non-HTTPS connections."""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class RequestHelper:
    __url: str = ""
    session_options: dict
    _log = log

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, log):
        self._log = log

    def __init__(self, headers: dict = None, **kargs):
        if headers is None:
            headers = {}
        self.session = requests.Session()
        self.headers = headers
        self.session_options = {'headers': self.headers}

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value: str):
        self.__url = value

    def _get(self, url, headers: dict = None) -> requests.Response:
        if headers is None:
            headers = {'headers': {}}
        silence_request_warnings()
        options = self.session_options.copy()
        options.update(headers)
        response = self.session.get(url, **options)
        self.log.debug(f"GET {url} response: {response.status_code}")
        return response

    def _continue_request(self, response, data: list, headers: dict) -> None:
        while True:
            _next = response['meta']['next']
            if _next:
                response = self._get(_next, headers).json()
                data += response['data']
            else:
                break

    def get(self, url, headers: dict = None) -> requests.Response:
        if headers is None:
            headers = {'headers': {}}
        url = self.url + url
        options = self.session_options.copy()
        options.update(headers)
        response = self._get(url, options)
        if response.status_code != 200:
            self.log.warning(f"{response.status_code}")
            if response.status_code > 500:
                pass
            else:
                pp(response.json())
        return response

    def post(self, url, data, headers: dict = None) -> requests.Response:
        if headers is None:
            headers = {'headers': {}}
        silence_request_warnings()
        url = self.url + url
        options = self.session_options.copy()
        options.update(headers)
        response = self.session.post(url, data=data, **options)
        log.debug(f'POST {url} response: {response.status_code}')
        return response

    def put_dict(self, url: str, data: dict) -> requests.Response:
        return self.put(url=url, data=dumps(data))

