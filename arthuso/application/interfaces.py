"""Application interface ports defining the Rental Research MCP boundary."""

from typing import Protocol
from arthuso.domain.primitives import PropertyId
from arthuso.domain.models import SearchCriteria, PaginationSpec, PropertyDetail
from arthuso.domain.collections import (
    PropertyCollection,
    CityCollection,
    NeighborhoodCollection,
    PropertyTypeCollection,
)


class RentalSearchPort(Protocol):
    """Port for executing rental searches."""

    def search_rentals(
        self, criteria: SearchCriteria, pagination: PaginationSpec
    ) -> PropertyCollection:
        """Executes rental search and returns collection of property items."""
        ...

    def search_by_url(self, target_url: str) -> PropertyCollection:
        """Parses a frontend search URL and executes the search."""
        ...


class PropertyDetailPort(Protocol):
    """Port for retrieving rich property details."""

    def get_property_by_id(self, post_id: PropertyId) -> PropertyDetail:
        """Retrieves full property detail model by WordPress post ID."""
        ...

    def get_property_by_slug(self, slug: str) -> PropertyDetail:
        """Retrieves full property detail model by slug."""
        ...


class FilterCatalogPort(Protocol):
    """Port for discovering available filter options."""

    def get_cities(self) -> CityCollection:
        """Retrieves all available cities."""
        ...

    def get_neighborhoods(self) -> NeighborhoodCollection:
        """Retrieves all available neighborhoods."""
        ...

    def get_property_types(self) -> PropertyTypeCollection:
        """Retrieves all available property types."""
        ...
