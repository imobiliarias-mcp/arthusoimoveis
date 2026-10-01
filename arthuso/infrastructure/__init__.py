"""Infrastructure package for Arthuso Imóveis rental research."""

from arthuso.infrastructure.endpoints import (
    BASE_URL,
    SEARCH_PATH,
    PROPERTIES_PATH,
    PROPERTY_STATUS_PATH,
    PROPERTY_CITY_PATH,
    PROPERTY_AREA_PATH,
    PROPERTY_TYPE_PATH,
    MEDIA_PATH,
    PAGE_SIZE,
    DEFAULT_HEADERS,
)
from arthuso.infrastructure.http_transport import (
    HttpTransportProtocol,
    HttpxTransport,
)
from arthuso.infrastructure.query_builder import SearchQueryBuilder
from arthuso.infrastructure.html_parser import SearchHtmlParser
from arthuso.infrastructure.deserializer import ResponseDeserializer

__all__ = [
    "BASE_URL",
    "SEARCH_PATH",
    "PROPERTIES_PATH",
    "PROPERTY_STATUS_PATH",
    "PROPERTY_CITY_PATH",
    "PROPERTY_AREA_PATH",
    "PROPERTY_TYPE_PATH",
    "MEDIA_PATH",
    "PAGE_SIZE",
    "DEFAULT_HEADERS",
    "HttpTransportProtocol",
    "HttpxTransport",
    "SearchQueryBuilder",
    "SearchHtmlParser",
    "ResponseDeserializer",
]
