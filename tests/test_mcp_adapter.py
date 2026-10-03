"""Unit tests for ArthusoMcpAdapter."""

from scripts.mcp.tools import ArthusoMcpAdapter


class DummyService:
    """Dummy service for testing Arthuso MCP adapter."""

    def search(self, criteria, pagination):
        class DummyProp:
            post_id = type("Id", (), {"value": 101})()
            title = "Apto Timóteo"
            price_text = "R$ 1.200"
            bedrooms = 2
            bathrooms = 1
            property_type = "Apartamento"
            url = "https://arthusoimoveis.com.br/imovel/101"
            images = ["https://arthusoimoveis.com.br/img.jpg"]
            location = "Centro"
        return [DummyProp()]

    def get_details(self, property_id):
        class DummyDetail:
            post_id = type("Id", (), {"value": int(property_id.value if hasattr(property_id, 'value') else property_id)})()
            title = "Apto Timóteo"
            price_text = "R$ 1.200"
            description = "Excelente apto"
            bedrooms = 2
            bathrooms = 1
            property_type = "Apartamento"
            url = "https://arthusoimoveis.com.br/imovel/101"
            images = ["https://arthusoimoveis.com.br/img.jpg"]
            location = "Centro"
        return DummyDetail()

    def get_cities(self):
        return [type("City", (), {"name": "timoteo", "label": "Timóteo"})()]


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    adapter = ArthusoMcpAdapter(service=DummyService())
    info = adapter.get_provider_info()
    assert info["provider_name"] == "arthusoimoveis"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    adapter = ArthusoMcpAdapter(service=DummyService())
    res = adapter.search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert isinstance(res, dict)
    assert res["provider"] == "arthusoimoveis"
    assert len(res["listings"]) == 1


def test_mcp_adapter_property_detail():
    """Test MCP property detail tool execution."""
    adapter = ArthusoMcpAdapter(service=DummyService())
    detail = adapter.get_property_detail("101")
    assert isinstance(detail, dict)
    assert detail["title"] == "Apto Timóteo"
