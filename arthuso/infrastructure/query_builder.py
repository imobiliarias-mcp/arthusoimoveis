"""Query builder translating SearchCriteria into URL parameters."""

from typing import Dict, Tuple
from arthuso.domain.models import SearchCriteria, PaginationSpec
from arthuso.infrastructure.endpoints import SEARCH_PATH


class SearchQueryBuilder:
    """Builds search query path and parameters from domain criteria."""

    def build_path(self, pagination: PaginationSpec) -> str:
        """Computes path based on pagination spec."""
        page_val = pagination.page.value
        if page_val > 1:
            return f"{SEARCH_PATH}page/{page_val}/"
        return SEARCH_PATH

    def build_parameters(self, criteria: SearchCriteria) -> Dict[str, str]:
        """Translates criteria into query parameter dictionary."""
        params: Dict[str, str] = {"status[0]": "alugar"}
        self._apply_location(params, criteria)
        self._apply_property_type(params, criteria)
        self._apply_rooms(params, criteria)
        self._apply_pricing(params, criteria)
        self._apply_identity_and_sort(params, criteria)
        return params

    def _apply_location(self, params: Dict[str, str], c: SearchCriteria) -> None:
        if c.city:
            params["location[0]"] = c.city.as_string()
        if c.neighborhood:
            params["areas[0]"] = c.neighborhood.as_string()

    def _apply_property_type(self, params: Dict[str, str], c: SearchCriteria) -> None:
        if c.property_type:
            params["type[0]"] = c.property_type.as_string()

    def _apply_rooms(self, params: Dict[str, str], c: SearchCriteria) -> None:
        if c.bedrooms:
            params["bedrooms"] = c.bedrooms.as_string()
        if c.bathrooms:
            params["bathrooms"] = c.bathrooms.as_string()

    def _apply_pricing(self, params: Dict[str, str], c: SearchCriteria) -> None:
        if c.min_price:
            params["min-price"] = c.min_price.as_integer_string()
        if c.max_price:
            params["max-price"] = c.max_price.as_integer_string()

    def _apply_identity_and_sort(self, params: Dict[str, str], c: SearchCriteria) -> None:
        if c.property_code:
            params["property_id"] = c.property_code.as_string()
        if c.keyword:
            params["keyword"] = c.keyword
        if c.sort_by:
            params["sortby"] = c.sort_by.as_string()

    def build_request(
        self, criteria: SearchCriteria, pagination: PaginationSpec
    ) -> Tuple[str, Dict[str, str]]:
        """Returns tuple of target path and query parameter dictionary."""
        path = self.build_path(pagination)
        params = self.build_parameters(criteria)
        return path, params
