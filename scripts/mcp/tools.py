"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from typing import Any
from arthuso import (
    HttpxTransport,
    ResponseDeserializer,
    RentalResearchService,
    SearchCriteria,
    PaginationSpec,
    PropertyId,
    CitySlug,
    BedroomCount,
    RentalPrice,
    PageNumber,
)


class ArthusoMcpAdapter:
    """Adapts Arthuso rental service for consumption by MCP servers and tool registries."""

    def __init__(self, service: Any = None) -> None:
        """Initialize adapter with an abstract rental service."""
        if service is not None:
            self._service = service
            return
        transport = HttpxTransport()
        deserializer = ResponseDeserializer()
        self._service = RentalResearchService(transport, deserializer)

    @classmethod
    def create_default(cls) -> "ArthusoMcpAdapter":
        """Factory constructor instantiating the default Arthuso provider."""
        return cls()

    def _build_criteria(self, city: str, max_price: float, bedrooms: int) -> SearchCriteria:
        """Build domain SearchCriteria from tool parameters."""
        c = CitySlug(city.lower()) if city else None
        b = BedroomCount(bedrooms) if bedrooms > 0 else None
        p = RentalPrice(max_price) if max_price > 0 else None
        return SearchCriteria(city=c, bedrooms=b, max_price=p)

    def search_rentals(
        self,
        city: str = "",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        """Execute a rental property search for an MCP tool call."""
        criteria = self._build_criteria(city, max_price, bedrooms)
        pagination = PaginationSpec(page=PageNumber(page))
        results = self._service.search(criteria, pagination)
        return self._format_collection(results)

    def _format_collection(self, collection: list[Any]) -> dict[str, Any]:
        """Format collection into standard dictionary."""
        return {
            "provider": "arthusoimoveis",
            "total_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format individual listing item."""
        pid = item.post_id.value if hasattr(item, "post_id") and item.post_id else ""
        return {
            "id": str(pid),
            "title": getattr(item, "title", ""),
            "price": getattr(item, "price_text", ""),
            "bedrooms": getattr(item, "bedrooms", 0),
            "bathrooms": getattr(item, "bathrooms", 0),
            "property_type": getattr(item, "property_type", ""),
            "url": getattr(item, "url", "") or getattr(item, "detail_url", ""),
            "photos": getattr(item, "images", []),
        }

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        pid = PropertyId(int(property_code)) if property_code.isdigit() else property_code
        detail = self._service.get_details(pid)
        return {
            "id": str(property_code),
            "title": getattr(detail, "title", ""),
            "description": getattr(detail, "description", ""),
            "price": getattr(detail, "price_text", ""),
            "bedrooms": getattr(detail, "bedrooms", 0),
            "bathrooms": getattr(detail, "bathrooms", 0),
            "property_type": getattr(detail, "property_type", ""),
            "url": getattr(detail, "url", ""),
            "photos": getattr(detail, "images", []),
        }

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        cities = self._service.get_cities()
        return {"cities": [{"name": getattr(c, "name", ""), "label": getattr(c, "label", "")} for c in cities]}

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": "arthusoimoveis",
            "coverage_region": "Timóteo, Coronel Fabriciano, Ipatinga",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }
