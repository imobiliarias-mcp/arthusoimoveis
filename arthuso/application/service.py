"""Primary service facade implementing the central Rental Research MCP boundary."""

from dataclasses import replace
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
    BASE_URL,
    MEDIA_PATH,
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


class RentalResponseParser:
    """Coordinate parsing of search HTML and property detail JSON."""

    def __init__(
        self, deserializer: ResponseDeserializer, public_base_url: str
    ) -> None:
        self._deserializer = deserializer
        self._search_parser = SearchHtmlParser(public_base_url)

    def parse_search(self, html_response: str) -> PropertyCollection:
        """Parse listing cards into a typed property collection."""
        return self._search_parser.parse_listings(html_response)

    def parse_detail(self, payload: dict[str, Any]) -> PropertyDetail:
        """Deserialize a property detail payload into its domain model."""
        return self._deserializer.deserialize_property_detail(payload)

    def parse_cities(self, payload: list[dict[str, Any]]) -> CityCollection:
        """Deserialize a city catalog into its typed collection."""
        return self._deserializer.deserialize_cities(payload)

    def parse_neighborhoods(
        self, payload: list[dict[str, Any]]
    ) -> NeighborhoodCollection:
        """Deserialize a neighborhood catalog into its typed collection."""
        return self._deserializer.deserialize_neighborhoods(payload)

    def parse_property_types(
        self, payload: list[dict[str, Any]]
    ) -> PropertyTypeCollection:
        """Deserialize a property type catalog into its typed collection."""
        return self._deserializer.deserialize_property_types(payload)


class RentalResearchService:
    """Central service coordinator for rental research MCP integration."""

    def __init__(
        self,
        http_transport: HttpTransportProtocol,
        deserializer: ResponseDeserializer,
        public_base_url: str = BASE_URL,
    ) -> None:
        self._http_transport = http_transport
        self._response_parser = RentalResponseParser(deserializer, public_base_url)

    def search_rentals(
        self, criteria: SearchCriteria, pagination: PaginationSpec
    ) -> PropertyCollection:
        """Performs rental search and returns collection of properties."""
        builder = SearchQueryBuilder()
        path, params = builder.build_request(criteria, pagination)
        html_response = self._http_transport.get_html(path, params)
        return self._response_parser.parse_search(html_response)

    def search_by_url(self, target_url: str) -> PropertyCollection:
        """Parses target URL and executes rental search."""
        parser = FrontendUrlParser()
        criteria, pagination = parser.parse_url(target_url)
        return self.search_rentals(criteria, pagination)

    def get_property_by_id(self, post_id: PropertyId) -> PropertyDetail:
        """Retrieves full property details by WordPress post ID."""
        detail_path = f"{PROPERTIES_PATH}/{post_id.value}"
        raw_data = self._http_transport.get_json(detail_path, {"_embed": "true"})
        return self._with_gallery(self._response_parser.parse_detail(raw_data))

    def get_property_by_slug(self, slug: str) -> PropertyDetail:
        """Retrieves full property details by slug."""
        params: Dict[str, Any] = {"slug": slug, "_embed": "true"}
        raw_list: List[Dict[str, Any]] = self._http_transport.get_json(PROPERTIES_PATH, params)
        if not raw_list:
            raise PropertyNotFoundError(f"Property with slug {slug} not found")
        first_item = raw_list[0]
        return self._with_gallery(self._response_parser.parse_detail(first_item))

    def _with_gallery(self, detail: PropertyDetail) -> PropertyDetail:
        """Attach gallery photo URLs resolved in one media request from the attachment ids."""
        image_ids = _gallery_ids(detail.meta)
        if not image_ids:
            return detail
        raw_media = self._http_transport.get_json(
            MEDIA_PATH, {"include": ",".join(image_ids), "per_page": 100}
        )
        urls_by_id = {str(item["id"]): item["source_url"] for item in raw_media if item.get("source_url")}
        images = [urls_by_id[image_id] for image_id in image_ids if image_id in urls_by_id]
        return replace(detail, summary=replace(detail.summary, images=images))

    def get_cities(self) -> CityCollection:
        """Retrieves all available cities."""
        params: Dict[str, Any] = {"per_page": 100}
        raw_list = self._http_transport.get_json(PROPERTY_CITY_PATH, params)
        return self._response_parser.parse_cities(raw_list)

    def get_neighborhoods(self) -> NeighborhoodCollection:
        """Retrieves all available neighborhoods."""
        params: Dict[str, Any] = {"per_page": 100}
        raw_list = self._http_transport.get_json(PROPERTY_AREA_PATH, params)
        return self._response_parser.parse_neighborhoods(raw_list)

    def get_property_types(self) -> PropertyTypeCollection:
        """Retrieves all available property types."""
        params: Dict[str, Any] = {"per_page": 100}
        raw_list = self._http_transport.get_json(PROPERTY_TYPE_PATH, params)
        return self._response_parser.parse_property_types(raw_list)


def _gallery_ids(meta: Dict[str, Any]) -> List[str]:
    """Return the numeric attachment ids of the property gallery, in display order."""
    raw_ids = meta.get("fave_property_images")
    if not isinstance(raw_ids, list):
        return []
    return [str(value) for value in raw_ids if str(value).isdigit()]
