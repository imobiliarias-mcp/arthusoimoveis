"""Regression tests for certificate verification in both HTTP operations."""

import ssl

import httpx
import pytest
from httpx import Client as NativeHttpxClient

from arthuso.infrastructure.http_transport import HttpxTransport

REQUEST_URL = "https://example.test/property/123"
RESPONSE_BODY = '{"available": true}'


def verified_client(**options):
    """Inspect the native client's TLS settings before stubbing network I/O."""
    client = NativeHttpxClient(**options)
    transport = client._transport
    connection_pool = transport._pool
    context = connection_pool._ssl_context
    client.close()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname
    adapter = httpx.MockTransport(
        lambda request: httpx.Response(200, text=RESPONSE_BODY)
    )
    return NativeHttpxClient(transport=adapter)


@pytest.mark.parametrize("operation", ("get_html", "get_json"))
def test_http_operations_require_verified_certificates(monkeypatch, operation):
    """HTML and JSON requests require certificate and hostname validation."""
    monkeypatch.setattr(httpx, "Client", verified_client)
    transport = HttpxTransport()
    result = getattr(transport, operation)(REQUEST_URL, {})
    assert result in (RESPONSE_BODY, {"available": True})
