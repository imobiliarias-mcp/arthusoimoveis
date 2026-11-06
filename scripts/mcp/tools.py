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
        results = self._service.search_rentals(criteria, pagination)
        return self._format_collection(results)

    def _format_collection(self, collection: Any) -> dict[str, Any]:
        """Format collection into standard dictionary."""
        return {
            "provider": "arthusoimoveis",
            "total_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format a PropertySummary into the standard listing dictionary."""
        return {
            "id": self._post_id_text(item.post_id),
            "title": item.title,
            "price": item.price_text,
            "bedrooms": item.bedrooms or 0,
            "bathrooms": item.bathrooms or 0,
            "property_type": item.property_type or "",
            "url": item.url or item.detail_url,
            "photos": list(item.images),
        }

    def _post_id_text(self, post_id: PropertyId | None) -> str:
        """Return the WordPress post id as text, or an empty string when absent."""
        if post_id is None:
            return ""
        return post_id.as_string()

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        detail = self._fetch_detail(property_code)
        summary = detail.summary
        return {
            "id": str(property_code),
            "title": summary.title,
            "description": detail.description,
            "price": summary.price_text,
            "bedrooms": summary.bedrooms or 0,
            "bathrooms": summary.bathrooms or 0,
            "property_type": summary.property_type or "",
            "url": summary.url or summary.detail_url,
            "photos": list(summary.images),
        }

    def _fetch_detail(self, property_code: str) -> Any:
        """Fetch a detail by numeric WordPress id, otherwise by slug."""
        if property_code.isdigit():
            return self._service.get_property_by_id(PropertyId(int(property_code)))
        return self._service.get_property_by_slug(property_code)

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        cities = self._service.get_cities()
        return {
            "cities": [
                {"name": city.name, "slug": city.slug, "count": city.count}
                for city in cities
            ]
        }

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": "arthusoimoveis",
            "coverage_region": "Timóteo, Coronel Fabriciano, Ipatinga",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }
