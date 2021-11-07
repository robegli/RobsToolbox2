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

