import requests
from typing import Any, Dict, Optional

API_BASE_URL = "http://web-api:4000"


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        response = self.session.request(
            method=method.upper(),
            url=self._url(path),
            params=params,
            json=json,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.text

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return self._request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return self._request("POST", path, json=json, headers=headers)

    def put(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return self._request("PUT", path, json=json, headers=headers)

    def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return self._request("DELETE", path, params=params, headers=headers)


client = APIClient()
