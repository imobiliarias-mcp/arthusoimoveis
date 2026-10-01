"""Primary service facade implementing the central Rental Research MCP boundary."""

from typing import Any, Dict, List
from arthuso.domain.primitives import PropertyId
from arthuso.domain.models import SearchCriteria, PaginationSpec, PropertyDetail
from arthuso.domain.collections import (
    PropertyCollection,
    CityCollection,
    NeighborhoodCollection,
    PropertyTypeCollection,
)
from arthuso.domain.exceptions import PropertyNotFoundError
from arthuso.infrastructure.endpoints import (
    PROPERTIES_PATH,
    PROPERTY_CITY_PATH,
    PROPERTY_AREA_PATH,
    PROPERTY_TYPE_PATH,
)
from arthuso.infrastructure.http_transport import HttpTransportProtocol
from arthuso.infrastructure.query_builder import SearchQueryBuilder
from arthuso.infrastructure.html_parser import SearchHtmlParser
from arthuso.infrastructure.deserializer import ResponseDeserializer
from arthuso.application.url_parser import FrontendUrlParser


class RentalResearchService:
    """Central service coordinator for rental research MCP integration."""

    def __init__(
        self,
        http_transport: HttpTransportProtocol,
        deserializer: ResponseDeserializer,
    ) -> None:
        self._http_transport = http_transport
        self._deserializer = deserializer

    def search_rentals(
        self, criteria: SearchCriteria, pagination: PaginationSpec
    ) -> PropertyCollection:
        """Performs rental search and returns collection of properties."""
        builder = SearchQueryBuilder()
        path, params = builder.build_request(criteria, pagination)
        html_response = self._http_transport.get_html(path, params)
        parser = SearchHtmlParser()
        return parser.parse_listings(html_response)

    def search_by_url(self, target_url: str) -> PropertyCollection:
        """Parses target URL and executes rental search."""
        parser = FrontendUrlParser()
        criteria, pagination = parser.parse_url(target_url)
        return self.search_rentals(criteria, pagination)

    def get_property_by_id(self, post_id: PropertyId) -> PropertyDetail:
        """Retrieves full property details by WordPress post ID."""
        detail_path = f"{PROPERTIES_PATH}/{post_id.value}"
        raw_data = self._http_transport.get_json(detail_path, {"_embed": "true"})
        return self._deserializer.deserialize_property_detail(raw_data)

    def get_property_by_slug(self, slug: str) -> PropertyDetail:
        """Retrieves full property details by slug."""
        params: Dict[str, Any] = {"slug": slug, "_embed": "true"}
        raw_list: List[Dict[str, Any]] = self._http_transport.get_json(PROPERTIES_PATH, params)
        if not raw_list:
            raise PropertyNotFoundError(f"Property with slug {slug} not found")
        first_item = raw_list[0]
        return self._deserializer.deserialize_property_detail(first_item)

    def get_cities(self) -> CityCollection:
        """Retrieves all available cities."""
        params: Dict[str, Any] = {"per_page": 100}
        raw_list = self._http_transport.get_json(PROPERTY_CITY_PATH, params)
        return self._deserializer.deserialize_cities(raw_list)

    def get_neighborhoods(self) -> NeighborhoodCollection:
        """Retrieves all available neighborhoods."""
        params: Dict[str, Any] = {"per_page": 100}
        raw_list = self._http_transport.get_json(PROPERTY_AREA_PATH, params)
        return self._deserializer.deserialize_neighborhoods(raw_list)

    def get_property_types(self) -> PropertyTypeCollection:
        """Retrieves all available property types."""
        params: Dict[str, Any] = {"per_page": 100}
        raw_list = self._http_transport.get_json(PROPERTY_TYPE_PATH, params)
        return self._deserializer.deserialize_property_types(raw_list)
