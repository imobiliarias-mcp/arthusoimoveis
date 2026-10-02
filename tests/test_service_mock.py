"""Unit tests for RentalResearchService using mock HTTP transport."""

from typing import Any, Dict
import pytest
from arthuso.domain.collections import PropertyCollection
from arthuso.domain.models import PropertySummary
from scripts import run_research
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

    def __init__(self, html_response: str = MOCK_HTML) -> None:
        self.last_path: str = ""
        self.last_params: Dict[str, Any] = {}
        self._html_response = html_response
        self.html_calls = 0
        self.json_calls = 0

    def get_html(self, path_or_url: str, params: Dict[str, Any]) -> str:
        self.html_calls += 1
        self.last_path = path_or_url
        self.last_params = params
        return self._html_response

    def get_json(self, path_or_url: str, params: Dict[str, Any]) -> Any:
        self.json_calls += 1
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


def test_property_collection_serializes_all_legacy_fields_and_count() -> None:
    """Serialize a public URL while retaining detail URL and listing fields."""
    listing = PropertySummary(
        post_id=PropertyId(39790),
        title="Apartamento Centro",
        detail_url="https://arthusoimoveis.com.br/property/apartamento-centro/",
        slug="apartamento-centro",
        price_text="R$ 950,00",
        bedrooms=2,
        bathrooms=1,
        property_type="Apartamento",
        images=["https://arthusoimoveis.com.br/photo.jpg"],
        property_code="1134",
    )

    serialized = PropertyCollection([listing, listing]).to_dictionary()

    assert serialized["returned_count"] == 2
    assert len(serialized["items"]) == 2
    assert serialized["items"][0]["url"] == listing.detail_url
    assert serialized["items"][0]["detail_url"] == listing.detail_url
    assert serialized["items"][0]["post_id"] == 39790
    assert serialized["items"][0]["property_code"] == "1134"
    assert serialized["items"][0]["images"] == listing.images


def test_serialized_public_url_preserves_raw_card_href() -> None:
    """Keep the legacy href while serializing the resolved public property URL."""
    listing = PropertySummary(
        post_id=None,
        title="Apartamento Centro",
        detail_url="/property/apartamento-centro/",
        slug="apartamento-centro",
        price_text="R$ 950,00",
        url="https://arthusoimoveis.com.br/property/apartamento-centro/",
    )

    serialized = PropertyCollection([listing]).to_dictionary()["items"][0]

    assert serialized["detail_url"] == "/property/apartamento-centro/"
    assert serialized["url"] == "https://arthusoimoveis.com.br/property/apartamento-centro/"


def test_empty_property_collection_serializes_zero_count() -> None:
    """Serialize an empty first-class collection with count zero."""
    serialized = PropertyCollection([]).to_dictionary()

    assert serialized["items"] == []
    assert serialized["returned_count"] == 0


def test_runner_prints_public_link_for_search_results(monkeypatch, capsys) -> None:
    """Print an existing search card link in the research runner output."""
    listing = PropertySummary(
        post_id=None,
        title="Apartamento Centro",
        detail_url="/property/apartamento-centro/",
        slug="apartamento-centro",
        price_text="R$ 950,00",
        url="https://public.example/property/apartamento-centro/",
    )

    class StubService:
        def __init__(self, transport, deserializer) -> None:
            pass

        def search_by_url(self, target_url: str) -> PropertyCollection:
            return PropertyCollection([listing])

        def get_cities(self) -> list:
            return []

        def get_neighborhoods(self) -> list:
            return []

        def get_property_types(self) -> list:
            return []

    monkeypatch.setattr(run_research, "HttpxTransport", object)
    monkeypatch.setattr(run_research, "ResponseDeserializer", object)
    monkeypatch.setattr(run_research, "RentalResearchService", StubService)

    result = run_research.main()

    assert result == 0
    assert "Link: https://public.example/property/apartamento-centro/" in capsys.readouterr().out


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


def test_service_passes_public_base_url_to_search_parser() -> None:
    """Resolve the card URL through the service and make no detail request."""
    relative_html = MOCK_HTML.replace(
        "https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/",
        "/property/configured/",
    )
    transport = MockHttpTransport(html_response=relative_html)
    service = RentalResearchService(
        transport, ResponseDeserializer(), public_base_url="https://public.example/"
    )

    result = service.search_rentals(SearchCriteria(), PaginationSpec())

    assert result[0].detail_url == "/property/configured/"
    assert result[0].url == "https://public.example/property/configured/"
    assert transport.html_calls == 1
    assert transport.json_calls == 0


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
