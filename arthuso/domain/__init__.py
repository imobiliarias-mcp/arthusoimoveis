"""Domain package for Arthuso Imóveis rental research."""

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
from arthuso.domain.models import (
    PropertySummary,
    PropertyDetail,
    SearchCriteria,
    PaginationSpec,
    TaxonomyTerm,
)
from arthuso.domain.collections import (
    PropertyCollection,
    CityCollection,
    NeighborhoodCollection,
    PropertyTypeCollection,
)
from arthuso.domain.exceptions import (
    ArthusoError,
    ValidationError,
    PropertyNotFoundError,
    HttpTransportError,
    ParsingError,
)

__all__ = [
    "PropertyId",
    "PropertyCode",
    "RentalPrice",
    "CitySlug",
    "NeighborhoodSlug",
    "PropertyTypeSlug",
    "BedroomCount",
    "BathroomCount",
    "PageNumber",
    "SortOrder",
    "PropertySummary",
    "PropertyDetail",
    "SearchCriteria",
    "PaginationSpec",
    "TaxonomyTerm",
    "PropertyCollection",
    "CityCollection",
    "NeighborhoodCollection",
    "PropertyTypeCollection",
    "ArthusoError",
    "ValidationError",
    "PropertyNotFoundError",
    "HttpTransportError",
    "ParsingError",
]
