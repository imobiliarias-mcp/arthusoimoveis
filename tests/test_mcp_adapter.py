"""Contract tests for ArthusoMcpAdapter running against the real RentalResearchService.

The fake transport only replaces network I/O. Service, parsers and domain models
are the production classes, so any drift in method names or model shape breaks here.
"""

from typing import Any

from arthuso.application.service import RentalResearchService
from arthuso.infrastructure.deserializer import ResponseDeserializer
from scripts.mcp.tools import ArthusoMcpAdapter

SEARCH_HTML = """
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

PROPERTY_JSON: dict[str, Any] = {
    "id": 39790,
    "slug": "apartamento-centro-timoteo",
    "link": "https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/",
    "title": {"rendered": "Apartamento Centro"},
    "content": {"rendered": "<p>Excelente apartamento</p>"},
    "property_meta": {
        "fave_property_price": ["950"],
        "fave_property_bedrooms": ["2"],
        "fave_property_bathrooms": ["1"],
    },
    "_embedded": {"wp:term": []},
}

CITIES_JSON = [{"id": 82, "name": "Timóteo", "slug": "timoteo", "count": 346}]


class FakeTransport:
    """HTTP transport serving the recorded Arthuso responses used by the adapter."""

    def get_html(self, path_or_url: str, params: dict[str, Any]) -> str:
        """Return the search results page."""
        return SEARCH_HTML

    def get_json(self, path_or_url: str, params: dict[str, Any]) -> Any:
        """Return REST payloads for detail, slug lookup and taxonomy endpoints."""
        if "property_city" in path_or_url:
            return CITIES_JSON
        if path_or_url.endswith("/wp-json/wp/v2/properties/39790"):
            return PROPERTY_JSON
        if params.get("slug") == "apartamento-centro-timoteo":
            return [PROPERTY_JSON]
        return []


def _build_adapter() -> ArthusoMcpAdapter:
    """Wire the adapter to the real service backed by the fake transport."""
    service = RentalResearchService(FakeTransport(), ResponseDeserializer())
    return ArthusoMcpAdapter(service=service)


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    info = _build_adapter().get_provider_info()
    assert info["provider_name"] == "arthusoimoveis"
    assert "search_rentals" in info["supported_operations"]


def test_search_rentals_maps_real_listing_fields():
    """Search must call the real service and map its PropertySummary fields."""
    res = _build_adapter().search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert res["provider"] == "arthusoimoveis"
    assert res["total_count"] == 1
    listing = res["listings"][0]
    assert listing["id"] == "39790"
    assert listing["title"] == "Apartamento Centro"
    assert listing["price"] == "R$ 950,00"
    assert listing["bedrooms"] == 2
    assert listing["url"] == "https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/"


def test_property_detail_by_numeric_id_uses_service_summary_and_description():
    """A numeric code must fetch by id and read title/price from the summary."""
    detail = _build_adapter().get_property_detail("39790")
    assert detail["id"] == "39790"
    assert detail["title"] == "Apartamento Centro"
    assert detail["price"] == "R$ 950"
    assert detail["bedrooms"] == 2
    assert detail["bathrooms"] == 1
    assert detail["description"] == "<p>Excelente apartamento</p>"
    assert detail["url"] == "https://arthusoimoveis.com.br/property/apartamento-centro-timoteo/"


def test_property_detail_by_slug_fetches_through_slug_lookup():
    """A non-numeric code must be treated as a slug."""
    detail = _build_adapter().get_property_detail("apartamento-centro-timoteo")
    assert detail["id"] == "apartamento-centro-timoteo"
    assert detail["title"] == "Apartamento Centro"
    assert detail["description"] == "<p>Excelente apartamento</p>"


def test_facets_expose_real_taxonomy_term_fields():
    """Facets must be built from TaxonomyTerm (name, slug, count) without a label."""
    facets = _build_adapter().get_facets()
    assert facets == {
        "cities": [{"name": "Timóteo", "slug": "timoteo", "count": 346}],
    }
