"""HTML parser extracting PropertySummary models from Houzez search markup."""

import json
from typing import List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
from arthuso.domain.exceptions import ParsingError
from arthuso.domain.models import PropertySummary
from arthuso.domain.primitives import PropertyId
from arthuso.domain.collections import PropertyCollection


class SearchHtmlParser:
    """Parses Houzez search result HTML into PropertyCollection."""

    def parse_listings(self, html_text: str) -> PropertyCollection:
        """Parses HTML document and extracts collection of property summaries."""
        if not html_text.strip():
            return PropertyCollection([])
        soup = BeautifulSoup(html_text, "html.parser")
        card_elements = soup.select(".item-listing-wrap")
        summaries: List[PropertySummary] = []
        for card in card_elements:
            summary = self._parse_single_card(card)
            summaries.append(summary)
        return PropertyCollection(summaries)

    def _extract_amenities(self, card: Tag) -> tuple[int | None, int | None, str | None]:
        beds = self._extract_numeric_amenity(card, ".h-beds .hz-figure")
        baths = self._extract_numeric_amenity(card, ".h-baths .hz-figure")
        prop_type = self._extract_text(card, ".h-type span")
        return beds, baths, prop_type

    def _parse_single_card(self, card: Tag) -> PropertySummary:
        post_id = self._extract_post_id(card)
        title, url, slug = self._extract_link_info(card)
        price = self._extract_price(card)
        beds, baths, prop_type = self._extract_amenities(card)
        images = self._extract_gallery_images(card)
        return PropertySummary(
            post_id, title, url, slug, price, beds, baths, prop_type, images
        )

    def _extract_post_id(self, card: Tag) -> Optional[PropertyId]:
        raw_id = card.get("data-listid")
        if raw_id and str(raw_id).isdigit():
            return PropertyId(int(str(raw_id)))
        hz_id = card.get("data-hz-id", "")
        clean_hz = str(hz_id).replace("hz-", "")
        if clean_hz.isdigit():
            return PropertyId(int(clean_hz))
        return None

    def _extract_link_info(self, card: Tag) -> tuple[str, str, str]:
        link_elem = card.select_one(".item-title a")
        if not link_elem:
            raise ParsingError("Missing item-title link element in card")
        title = link_elem.get_text(strip=True)
        url = str(link_elem.get("href", ""))
        slug = self._extract_slug(url)
        return title, url, slug

    def _extract_slug(self, url: str) -> str:
        parsed = urlparse(url)
        path_segments = [p for p in parsed.path.split("/") if p]
        if path_segments:
            return path_segments[-1]
        return ""

    def _extract_price(self, card: Tag) -> str:
        elem = card.select_one(".item-price")
        if elem:
            return elem.get_text(strip=True)
        return ""

    def _extract_numeric_amenity(self, card: Tag, selector: str) -> Optional[int]:
        elem = card.select_one(selector)
        if not elem:
            return None
        text_val = elem.get_text(strip=True)
        if text_val.isdigit():
            return int(text_val)
        return None

    def _extract_text(self, card: Tag, selector: str) -> Optional[str]:
        elem = card.select_one(selector)
        if not elem:
            return None
        return elem.get_text(strip=True)

    def _extract_gallery_images(self, card: Tag) -> List[str]:
        raw_data = card.get("data-images")
        if not raw_data:
            return []
        try:
            image_list = json.loads(str(raw_data))
            return [item.get("image") for item in image_list if item.get("image")]
        except json.JSONDecodeError:
            return []
