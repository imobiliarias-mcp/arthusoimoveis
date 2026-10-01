"""Domain models representing rental entities and search criteria."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from arthuso.domain.primitives import (
    PropertyId,
    PropertyCode,
    RentalPrice,
    CitySlug,
    NeighborhoodSlug,
    PropertyTypeSlug,
    BedroomCount,
    BathroomCount,
    PageNumber,
    SortOrder,
)


@dataclass(frozen=True)
class PaginationSpec:
    """Specification for page pagination."""

    page: PageNumber = field(default_factory=lambda: PageNumber(1))


@dataclass(frozen=True)
class SearchCriteria:
    """Encapsulates criteria for rental property searches."""

    city: Optional[CitySlug] = None
    neighborhood: Optional[NeighborhoodSlug] = None
    property_type: Optional[PropertyTypeSlug] = None
    bedrooms: Optional[BedroomCount] = None
    bathrooms: Optional[BathroomCount] = None
    min_price: Optional[RentalPrice] = None
    max_price: Optional[RentalPrice] = None
    property_code: Optional[PropertyCode] = None
    keyword: Optional[str] = None
    sort_by: Optional[SortOrder] = None


@dataclass(frozen=True)
class PropertySummary:
    """Encapsulates key summary attributes of a rental property."""

    post_id: Optional[PropertyId]
    title: str
    detail_url: str
    slug: str
    price_text: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    property_type: Optional[str] = None
    images: List[str] = field(default_factory=list)
    property_code: Optional[str] = None


@dataclass(frozen=True)
class PropertyDetail:
    """Encapsulates detailed attributes of a rental property."""

    summary: PropertySummary
    description: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)
    terms: Dict[str, List[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class TaxonomyTerm:
    """Represents a taxonomy term (city, neighborhood, status, type)."""

    term_id: int
    name: str
    slug: str
    count: int
