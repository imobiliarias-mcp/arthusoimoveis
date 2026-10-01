"""Domain primitive value objects for Arthuso rental research."""

from dataclasses import dataclass
from arthuso.domain.exceptions import ValidationError


@dataclass(frozen=True)
class PropertyId:
    """Encapsulates a valid WordPress property post ID."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValidationError(f"Property ID must be positive: {self.value}")

    def as_string(self) -> str:
        """Returns string representation of property ID."""
        return str(self.value)


@dataclass(frozen=True)
class PropertyCode:
    """Encapsulates a real estate agency property reference code."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip()
        if not cleaned:
            raise ValidationError("Property code cannot be empty")

    def as_string(self) -> str:
        """Returns normalized string representation of property code."""
        return self.value.strip()


@dataclass(frozen=True)
class RentalPrice:
    """Encapsulates a rental monetary amount in Brazilian Reais."""

    amount: float

    def __post_init__(self) -> None:
        if self.amount < 0.0:
            raise ValidationError(f"Rental price cannot be negative: {self.amount}")

    def as_integer_string(self) -> str:
        """Returns integer string for query parameter encoding."""
        return str(int(self.amount))


@dataclass(frozen=True)
class CitySlug:
    """Encapsulates a normalized city identifier slug."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip().lower()
        if not cleaned:
            raise ValidationError("City slug cannot be empty")

    def as_string(self) -> str:
        """Returns normalized city slug."""
        return self.value.strip().lower()


@dataclass(frozen=True)
class NeighborhoodSlug:
    """Encapsulates a normalized neighborhood (bairro) identifier slug."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip().lower()
        if not cleaned:
            raise ValidationError("Neighborhood slug cannot be empty")

    def as_string(self) -> str:
        """Returns normalized neighborhood slug."""
        return self.value.strip().lower()


@dataclass(frozen=True)
class PropertyTypeSlug:
    """Encapsulates a normalized property type slug."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip().lower()
        if not cleaned:
            raise ValidationError("Property type slug cannot be empty")

    def as_string(self) -> str:
        """Returns normalized property type slug."""
        return self.value.strip().lower()


@dataclass(frozen=True)
class BedroomCount:
    """Encapsulates bedroom count constraint."""

    count: int

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValidationError(f"Bedroom count cannot be negative: {self.count}")

    def as_string(self) -> str:
        """Returns string representation of bedroom count."""
        return str(self.count)


@dataclass(frozen=True)
class BathroomCount:
    """Encapsulates bathroom count constraint."""

    count: int

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValidationError(f"Bathroom count cannot be negative: {self.count}")

    def as_string(self) -> str:
        """Returns string representation of bathroom count."""
        return str(self.count)


@dataclass(frozen=True)
class PageNumber:
    """Encapsulates a 1-indexed pagination number."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValidationError(f"Page number must be at least 1: {self.value}")

    def as_string(self) -> str:
        """Returns string representation of page number."""
        return str(self.value)


@dataclass(frozen=True)
class SortOrder:
    """Encapsulates supported sorting order."""

    value: str

    _ALLOWED = ("a_price", "d_price", "d_date", "a_date")

    def __post_init__(self) -> None:
        if self.value not in self._ALLOWED:
            raise ValidationError(f"Unsupported sort order: {self.value}")

    def as_string(self) -> str:
        """Returns sort order string."""
        return self.value
