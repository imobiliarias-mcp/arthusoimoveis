"""Domain models representing rental entities and search criteria."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit
from arthuso.domain.exceptions import ValidationError
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

IMAGE_FILE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif")
NON_PROPERTY_ROUTE_PREFIXES = ("/wp-json/", "/wp-admin/admin-ajax.php")


def is_valid_public_property_url(url: str) -> bool:
    """Validate an absolute listing link and exclude known API, search, or image URLs."""
    try:
        parsed_url = urlsplit(url)
        hostname = parsed_url.hostname
        port = parsed_url.port
        username = parsed_url.username
        password = parsed_url.password
    except ValueError:
        return False
    path = parsed_url.path.lower()
    if parsed_url.scheme.lower() not in {"http", "https"} or not hostname:
        return False
    if username is not None or password is not None:
        return False
    if any(character.isspace() for character in parsed_url.netloc):
        return False
    if parsed_url.netloc.endswith(":") or (port is not None and port < 0):
        return False
    return not path.startswith(NON_PROPERTY_ROUTE_PREFIXES) and not path.endswith(
        IMAGE_FILE_SUFFIXES
    ) and not (path.rstrip("/") == "/busca" or path.startswith("/busca/"))


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
    url: str | None = None

    def to_dictionary(self) -> dict[str, Any]:
        """Serialize all fields while retaining the original href and public URL."""
        public_url = self.url or self.detail_url
        self._validate_detail_url(public_url)
        serialized = asdict(self)
        serialized["post_id"] = self.post_id.value if self.post_id else None
        serialized["url"] = public_url
        return serialized

    def _validate_detail_url(self, public_url: str) -> None:
        """Require a safe public property page before serializing a listing."""
        if is_valid_public_property_url(public_url):
            return
        identifier = self.post_id.as_string() if self.post_id else self.slug
        raise ValidationError(
            f"Property {identifier} has invalid public URL {public_url!r}."
        )


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
