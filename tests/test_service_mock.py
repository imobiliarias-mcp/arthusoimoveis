"""Unit tests for RentalResearchService using mock HTTP transport."""

from typing import Any, Dict
import pytest
from arthuso.domain.exceptions import PropertyNotFoundError
from arthuso.domain.models import SearchCriteria, PaginationSpec
from arthuso.domain.primitives import PropertyId, CitySlug, BedroomCount
from arthuso.infrastructure.deserializer import ResponseDeserializer
from arthuso.application.service import RentalResearchService

MOCK_HTML = """
<div class="item-listing-wrap hz-item-gallery-js card" data-listid="39790">
  <div class="item-wrap">
    <li class="item-price">R$ 950,00</li>
    <h2 class="item-title">
      <a href="https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/">
        Apartamento Centro
      </a>
    </h2>
    <ul class="item-amenities">
      <li class="h-beds"><span class="hz-figure">2</span></li>
    </ul>
  </div>
</div>
"""


class MockHttpTransport:
    """Mock implementation of HttpTransportProtocol."""

    def __init__(self) -> None:
        self.last_path: str = ""
        self.last_params: Dict[str, Any] = {}

    def get_html(self, path_or_url: str, params: Dict[str, Any]) -> str:
        self.last_path = path_or_url
        self.last_params = params
        return MOCK_HTML

    def get_json(self, path_or_url: str, params: Dict[str, Any]) -> Any:
        self.last_path = path_or_url
        self.last_params = params
        if "property_city" in path_or_url:
            return [{"id": 82, "name": "Timóteo", "slug": "timoteo", "count": 346}]
        if "property_area" in path_or_url:
            return [{"id": 89, "name": "Centro", "slug": "centro", "count": 45}]
        if "property_type" in path_or_url:
            return [{"id": 74, "name": "Apartamento", "slug": "apartamento", "count": 217}]
        if "properties/39790" in path_or_url:
            return {
                "id": 39790,
                "slug": "apartamento-centro-timoteo",
                "link": "https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/",
                "title": {"rendered": "Apartamento Centro"},
                "content": {"rendered": "<p>Content</p>"},
                "property_meta": {"fave_property_price": ["950"]},
                "_embedded": {"wp:term": []},
            }
        if "slug" in params:
            if params["slug"] == "apartamento-centro-timoteo":
                return [{
                    "id": 39790,
                    "slug": "apartamento-centro-timoteo",
                    "link": "https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/",
                    "title": {"rendered": "Apartamento Centro"},
                    "content": {"rendered": "<p>Content</p>"},
                    "property_meta": {"fave_property_price": ["950"]},
                    "_embedded": {"wp:term": []},
                }]
            return []
        return []


def test_service_search_rentals() -> None:
    transport = MockHttpTransport()
    deserializer = ResponseDeserializer()
    service = RentalResearchService(transport, deserializer)
    criteria = SearchCriteria(city=CitySlug("timoteo"), bedrooms=BedroomCount(2))
    results = service.search_rentals(criteria, PaginationSpec())
    assert len(results) == 1
    assert results[0].post_id is not None
    assert results[0].post_id.value == 39790
    assert transport.last_params["location[0]"] == "timoteo"
    assert transport.last_params["bedrooms"] == "2"


def test_service_get_property_by_id() -> None:
    transport = MockHttpTransport()
    deserializer = ResponseDeserializer()
    service = RentalResearchService(transport, deserializer)
    detail = service.get_property_by_id(PropertyId(39790))
    assert detail.summary.post_id is not None
    assert detail.summary.post_id.value == 39790
    assert "950" in detail.summary.price_text


def test_service_get_property_by_slug_success() -> None:
    transport = MockHttpTransport()
    deserializer = ResponseDeserializer()
    service = RentalResearchService(transport, deserializer)
    detail = service.get_property_by_slug("apartamento-centro-timoteo")
    assert detail.summary.slug == "apartamento-centro-timoteo"


def test_service_get_property_by_slug_not_found() -> None:
    transport = MockHttpTransport()
    deserializer = ResponseDeserializer()
    service = RentalResearchService(transport, deserializer)
    with pytest.raises(PropertyNotFoundError):
        service.get_property_by_slug("non-existent-property")


def test_service_filter_catalogs() -> None:
    transport = MockHttpTransport()
    deserializer = ResponseDeserializer()
    service = RentalResearchService(transport, deserializer)
    cities = service.get_cities()
    areas = service.get_neighborhoods()
    types = service.get_property_types()
    assert len(cities) == 1 and cities[0].slug == "timoteo"
    assert len(areas) == 1 and areas[0].slug == "centro"
    assert len(types) == 1 and types[0].slug == "apartamento"
