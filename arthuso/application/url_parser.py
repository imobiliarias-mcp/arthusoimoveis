"""Parser extracting SearchCriteria and PaginationSpec from frontend search URLs."""

import re
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse
from arthuso.domain.models import SearchCriteria, PaginationSpec
from arthuso.domain.primitives import (
    CitySlug,
    NeighborhoodSlug,
    PropertyTypeSlug,
    BedroomCount,
    BathroomCount,
    RentalPrice,
    PropertyCode,
    PageNumber,
    SortOrder,
)


class FrontendUrlParser:
    """Parses frontend search URLs into domain criteria and pagination specs."""

    def parse_url(self, target_url: str) -> Tuple[SearchCriteria, PaginationSpec]:
        """Deconstructs URL into SearchCriteria and PaginationSpec."""
        parsed = urlparse(target_url)
        query_dict = parse_qs(parsed.query)
        page_num = self._extract_page_number(parsed.path, query_dict)
        criteria = self._build_criteria(query_dict)
        return criteria, PaginationSpec(page=page_num)

    def _extract_page_number(
        self, path: str, query: Dict[str, List[str]]
    ) -> PageNumber:
        page_match = re.search(r"/page/(\d+)/?", path)
        if page_match:
            return PageNumber(int(page_match.group(1)))
        paged_param = self._get_single_val(query, "paged")
        if paged_param and paged_param.isdigit():
            return PageNumber(int(paged_param))
        return PageNumber(1)

    def _build_criteria(self, q: Dict[str, List[str]]) -> SearchCriteria:
        city = self._parse_slug(q, ["location[]", "location[0]", "location"], CitySlug)
        area = self._parse_slug(q, ["areas[]", "areas[0]", "areas"], NeighborhoodSlug)
        prop_type = self._parse_slug(q, ["type[]", "type[0]", "type"], PropertyTypeSlug)
        beds = self._parse_int(q, "bedrooms", BedroomCount)
        baths = self._parse_int(q, "bathrooms", BathroomCount)
        return self._assemble_criteria(q, city, area, prop_type, beds, baths)

    def _assemble_criteria(
        self, q: Dict[str, List[str]], city: Any, area: Any, ptype: Any, beds: Any, baths: Any
    ) -> SearchCriteria:
        min_p = self._parse_price(q, "min-price")
        max_p = self._parse_price(q, "max-price")
        code = self._parse_code(q, "property_id")
        kw = self._get_single_val(q, "keyword")
        sort = self._parse_sort(q)
        return SearchCriteria(city, area, ptype, beds, baths, min_p, max_p, code, kw, sort)

    def _get_single_val(self, q: Dict[str, List[str]], key: str) -> str | None:
        values = q.get(key, [])
        if values and values[0].strip():
            return values[0].strip()
        return None

    def _parse_slug(self, q: Dict[str, List[str]], keys: List[str], type_cls: type) -> Any:
        for k in keys:
            val = self._get_single_val(q, k)
            if val:
                return type_cls(val)
        return None

    def _parse_int(self, q: Dict[str, List[str]], key: str, type_cls: type) -> Any:
        val = self._get_single_val(q, key)
        if val and val.isdigit():
            return type_cls(int(val))
        return None

    def _parse_price(self, q: Dict[str, List[str]], key: str) -> RentalPrice | None:
        val = self._get_single_val(q, key)
        if val and val.replace(".", "", 1).isdigit():
            return RentalPrice(float(val))
        return None

    def _parse_code(self, q: Dict[str, List[str]], key: str) -> PropertyCode | None:
        val = self._get_single_val(q, key)
        if val:
            return PropertyCode(val)
        return None

    def _parse_sort(self, q: Dict[str, List[str]]) -> SortOrder | None:
        val = self._get_single_val(q, "sortby")
        if val in ("a_price", "d_price", "d_date", "a_date"):
            return SortOrder(val)
        return None
