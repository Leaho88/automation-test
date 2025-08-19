import requests
import time
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

logger = logging.getLogger(__name__)
class APIException(Exception):
    """ Custom exception for API-related error """
    def __init__(self, message: str, status_code: int=None, response: requests.Response= None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class BaseApiClient:
    """
    Features:
    - Session management for connection reuse
    - Automatic JSON handling
    - Built-in retry logic
    - Basic error handling
    """
    def __init__(self, base_url: str, timeout: int=30, max_retries: int = 3):
        self.base_url = base_url.strip('/')
        self.timeout = timeout
        self.max_retries = max_retries

        # Create persistent session
        self.session = requests.Session()

        # set default header
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "QA-Automation-Python/1.0"
            }
        )
    def set_auth_header(self, token: str, authen_type: str='Bearer'):
        """ Set authentication header for all requests"""
        self.session.headers['Authorization'] = f'{authen_type} {token}'

    def _build_url(self, endpoint: str) -> str:
        return urljoin(f'{self.base_url}/', endpoint.lstrip('/'))

    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        last_exception = None
        print(f"Making method {method} request to {url}")
        for attempt in (range(self.max_retries + 1)):
            try: 
                response = self.session.request(
                    method = method,
                    url = url,
                    timeout = self.timeout,
                    **kwargs
                )
                print(f"Response: {response.status_code}")
                return response
            except requests.exceptions.RequestException as e:
                last_exception = e
                print(f"Request attempt {attempt + 1} failed: {str(e)}")

                if(attempt < self.max_retries):
                    sleep_time = 2 ** attempt
                    print(f"retry in {sleep_time} seconds")
                    time.sleep(sleep_time)
        # All retry attempt failed
        raise APIException(f"Request failed after {self.max_retries} attempt: {str(last_exception)}")

    def _handle_response(self, response: requests.Response, expected_status: Union[int, list] = None):
        if expected_status is not None:
            if isinstance(expected_status, int):
                expected_status = [expected_status]
            if response.status_code not in expected_status:
                raise APIException(f"Expected status {expected_status} not found, got {response.status_code}, response: {response.text}", response.status_code, response)

        if response.status_code >= 400:
            raise APIException(
                f"HTTP Error {response.status_code}: {response.text}",
                response.status_code, 
                response
            )

        return response

    def get(self, endpoint: str, params: Dict = None, expected_status: int = 200) -> requests.Response:
        url = self._build_url(self.base_url, endpoint)
        response = self._make_request_with_retry("GET", url, params)
        return self._handle_response(response, expected_status)

    def post(self, endpoint: str, json_data: dict=None, expected_status: int=200) -> requests.Response:
        url = self._build_url(endpoint)
        response = self._make_request_with_retry("POST", url, json_data)
        return self._handle_response(response, expected_status)

    def get_json(
        self, endpoint: str, params: Dict = None, expected_result: int = 200
    ) -> Dict:
        response = self.get(endpoint, params, expected_result)
        try:
            return response.json()
        except:
            raise APIException("Response error", response.status_code, response)


def main():
    help(requests.Session().request)

if __name__== "__main__":
    main()
