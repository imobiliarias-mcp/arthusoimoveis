"""HTTP transport abstraction with Mod_Security header compliance."""

from typing import Any, Dict, Protocol
import httpx
from arthuso.domain.exceptions import HttpTransportError
from arthuso.infrastructure.endpoints import BASE_URL, DEFAULT_HEADERS


class HttpTransportProtocol(Protocol):
    """Protocol for HTTP client operations."""

    def get_html(self, path_or_url: str, params: Dict[str, Any]) -> str:
        """Executes GET request returning HTML response string."""
        ...

    def get_json(self, path_or_url: str, params: Dict[str, Any]) -> Any:
        """Executes GET request returning parsed JSON data."""
        ...


class HttpxTransport:
    """Robust HTTP transport using httpx conforming to Mod_Security requirements."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = 20.0) -> None:
        self._base_url = base_url
        self._timeout = timeout

    def _resolve_url(self, path_or_url: str) -> str:
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            return path_or_url
        clean_path = path_or_url.lstrip("/")
        return f"{self._base_url}/{clean_path}"

    def get_html(self, path_or_url: str, params: Dict[str, Any]) -> str:
        """Executes GET request and returns HTML text."""
        target_url = self._resolve_url(path_or_url)
        try:
            with httpx.Client(
                headers=DEFAULT_HEADERS,
                timeout=self._timeout,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = client.get(target_url, params=params)
                self._check_status(response)
                return response.text
        except httpx.HTTPError as err:
            raise HttpTransportError(f"HTTP request failed: {err}") from err

    def get_json(self, path_or_url: str, params: Dict[str, Any]) -> Any:
        """Executes GET request and returns parsed JSON object."""
        target_url = self._resolve_url(path_or_url)
        try:
            with httpx.Client(
                headers=DEFAULT_HEADERS,
                timeout=self._timeout,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = client.get(target_url, params=params)
                self._check_status(response)
                return response.json()
        except httpx.HTTPError as err:
            raise HttpTransportError(f"HTTP JSON request failed: {err}") from err

    def _check_status(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise HttpTransportError(
                f"Server returned error code {response.status_code}: {response.text[:200]}"
            )
