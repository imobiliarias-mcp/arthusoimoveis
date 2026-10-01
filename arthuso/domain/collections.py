"""First-class collections for rental domain entities."""

from typing import Iterator, Sequence, Tuple
from arthuso.domain.models import PropertySummary, TaxonomyTerm


class PropertyCollection:
    """First-class collection wrapping a sequence of PropertySummary items."""

    def __init__(self, items: Sequence[PropertySummary]) -> None:
        self._items: Tuple[PropertySummary, ...] = tuple(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[PropertySummary]:
        return iter(self._items)

    def __getitem__(self, index: int) -> PropertySummary:
        return self._items[index]

    def is_empty(self) -> bool:
        """Returns True if the collection contains no properties."""
        return len(self._items) == 0


class CityCollection:
    """First-class collection wrapping city taxonomy terms."""

    def __init__(self, items: Sequence[TaxonomyTerm]) -> None:
        self._items: Tuple[TaxonomyTerm, ...] = tuple(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[TaxonomyTerm]:
        return iter(self._items)

    def __getitem__(self, index: int) -> TaxonomyTerm:
        return self._items[index]


class NeighborhoodCollection:
    """First-class collection wrapping neighborhood taxonomy terms."""

    def __init__(self, items: Sequence[TaxonomyTerm]) -> None:
        self._items: Tuple[TaxonomyTerm, ...] = tuple(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[TaxonomyTerm]:
        return iter(self._items)

    def __getitem__(self, index: int) -> TaxonomyTerm:
        return self._items[index]


class PropertyTypeCollection:
    """First-class collection wrapping property type taxonomy terms."""

    def __init__(self, items: Sequence[TaxonomyTerm]) -> None:
        self._items: Tuple[TaxonomyTerm, ...] = tuple(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[TaxonomyTerm]:
        return iter(self._items)

    def __getitem__(self, index: int) -> TaxonomyTerm:
        return self._items[index]
