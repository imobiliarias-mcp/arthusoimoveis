"""Deserializer transforming REST API JSON responses into domain entities."""

from typing import Any, Dict, List
from urllib.parse import urlparse
from arthuso.domain.models import PropertySummary, PropertyDetail, TaxonomyTerm
from arthuso.domain.primitives import PropertyId
from arthuso.domain.collections import (
    PropertyCollection,
    CityCollection,
    NeighborhoodCollection,
    PropertyTypeCollection,
)


class ResponseDeserializer:
    """Deserializes raw API JSON into rich domain entities."""

    def deserialize_taxonomy_terms(self, data: List[Dict[str, Any]]) -> List[TaxonomyTerm]:
        """Deserializes raw taxonomy term list into TaxonomyTerm models."""
        terms: List[TaxonomyTerm] = []
        for item in data:
            terms.append(
                TaxonomyTerm(
                    term_id=int(item.get("id", 0)),
                    name=str(item.get("name", "")),
                    slug=str(item.get("slug", "")),
                    count=int(item.get("count", 0)),
                )
            )
        return terms

    def deserialize_cities(self, data: List[Dict[str, Any]]) -> CityCollection:
        """Transforms term data into CityCollection."""
        return CityCollection(self.deserialize_taxonomy_terms(data))

    def deserialize_neighborhoods(self, data: List[Dict[str, Any]]) -> NeighborhoodCollection:
        """Transforms term data into NeighborhoodCollection."""
        return NeighborhoodCollection(self.deserialize_taxonomy_terms(data))

    def deserialize_property_types(self, data: List[Dict[str, Any]]) -> PropertyTypeCollection:
        """Transforms term data into PropertyTypeCollection."""
        return PropertyTypeCollection(self.deserialize_taxonomy_terms(data))

    def deserialize_property_detail(self, data: Dict[str, Any]) -> PropertyDetail:
        """Transforms property REST JSON into PropertyDetail."""
        summary = self.deserialize_single_property(data)
        content_rendered = data.get("content", {}).get("rendered", "")
        meta = data.get("property_meta", {})
        terms = self._extract_embedded_terms(data)
        return PropertyDetail(
            summary=summary,
            description=content_rendered,
            meta=meta,
            terms=terms,
        )

    def deserialize_properties(self, data: List[Dict[str, Any]]) -> PropertyCollection:
        """Transforms REST property list into PropertyCollection."""
        items: List[PropertySummary] = []
        for item in data:
            items.append(self.deserialize_single_property(item))
        return PropertyCollection(items)

    def _extract_meta_summary(
        self, meta: Dict[str, Any]
    ) -> tuple[str, int | None, int | None, str]:
        price_val = self._first_meta_value(meta, "fave_property_price")
        price_str = f"R$ {price_val}" if price_val else ""
        beds = self._meta_int(meta, "fave_property_bedrooms")
        baths = self._meta_int(meta, "fave_property_bathrooms")
        code = self._first_meta_value(meta, "fave_property_id")
        return price_str, beds, baths, code

    def deserialize_single_property(self, item: Dict[str, Any]) -> PropertySummary:
        """Transforms a single REST property item into PropertySummary."""
        post_id = PropertyId(int(item["id"]))
        title = item.get("title", {}).get("rendered", "")
        url = item.get("link", "")
        slug = item.get("slug", self._slug_from_url(url))
        meta = item.get("property_meta", {})
        price, beds, baths, code = self._extract_meta_summary(meta)
        return PropertySummary(post_id, title, url, slug, price, beds, baths, None, [], code)

    def _extract_embedded_terms(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        terms_dict: Dict[str, List[str]] = {}
        embedded = data.get("_embedded", {})
        wp_terms = embedded.get("wp:term", [])
        for term_group in wp_terms:
            for term in term_group:
                tax = term.get("taxonomy", "unknown")
                name = term.get("name", "")
                terms_dict.setdefault(tax, []).append(name)
        return terms_dict

    def _first_meta_value(self, meta: Dict[str, Any], key: str) -> str:
        values = meta.get(key, [])
        if values and isinstance(values, list) and values[0]:
            return str(values[0])
        return ""

    def _meta_int(self, meta: Dict[str, Any], key: str) -> int | None:
        val = self._first_meta_value(meta, key)
        if val.isdigit():
            return int(val)
        return None

    def _slug_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        segments = [s for s in parsed.path.split("/") if s]
        if segments:
            return segments[-1]
        return ""
