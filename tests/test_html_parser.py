"""Unit tests for SearchHtmlParser."""

import pytest

from arthuso.domain.exceptions import ParsingError
from arthuso.infrastructure.html_parser import SearchHtmlParser

SAMPLE_CARD_HTML = """
<div class="item-listing-wrap hz-item-gallery-js card" data-hz-id="hz-39790" data-listid="39790"
     data-images='[{"image":"https://arthusoimoveis.com.br/img1.jpeg","alt":"","width":592,"height":444},
                   {"image":"https://arthusoimoveis.com.br/img2.jpeg","alt":"","width":592,"height":444}]'>
  <div class="item-wrap">
    <div class="item-header">
      <li class="item-price">R$ 950,00</li>
    </div>
    <div class="item-body">
      <h2 class="item-title">
        <a href="https://arthusoimoveis.com.br/property/apartamento-locacao-centro-timoteo/">
          Apartamento disponível para locação no Centro Norte, Timóteo
        </a>
      </h2>
      <ul class="item-amenities">
        <li class="h-beds"><span class="hz-figure">2</span></li>
        <li class="h-baths"><span class="hz-figure">1</span></li>
        <li class="h-type"><span>Apartamento</span></li>
      </ul>
    </div>
  </div>
</div>
"""


@pytest.mark.parametrize(
    ("card_url", "expected_url"),
    [
        (
            "https://arthusoimoveis.com.br/property/absolute/",
            "https://arthusoimoveis.com.br/property/absolute/",
        ),
        (
            "/property/relative/",
            "https://arthusoimoveis.com.br/property/relative/",
        ),
        (
            "//arthusoimoveis.com.br/property/protocol-relative/",
            "https://arthusoimoveis.com.br/property/protocol-relative/",
        ),
        ("?id=608", "https://arthusoimoveis.com.br/?id=608"),
    ],
)
def test_parse_listings_resolves_card_url(card_url: str, expected_url: str) -> None:
    """Resolve public links from the listing card without detail lookups."""
    card = SAMPLE_CARD_HTML.replace(
        "https://arthusoimoveis.com.br/property/apartamento-locacao-centro-timoteo/",
        card_url,
    )

    listing = SearchHtmlParser().parse_listings(card)[0]

    assert listing.detail_url == card_url
    assert listing.url == expected_url


def test_parse_listings_uses_injected_public_base_url() -> None:
    """Resolve relative card URLs against configured public origin."""
    card = SAMPLE_CARD_HTML.replace(
        "https://arthusoimoveis.com.br/property/apartamento-locacao-centro-timoteo/",
        "/property/configured/",
    )

    listing = SearchHtmlParser(public_base_url="https://public.example/").parse_listings(card)[0]

    assert listing.detail_url == "/property/configured/"
    assert listing.url == "https://public.example/property/configured/"


@pytest.mark.parametrize("card_url", ["javascript:alert(1)", ""])
def test_parse_listings_rejects_unrecoverable_url(card_url: str) -> None:
    """Reject invalid and absent links with the card identifier in context."""
    card = SAMPLE_CARD_HTML.replace(
        "https://arthusoimoveis.com.br/property/apartamento-locacao-centro-timoteo/",
        card_url,
    )

    with pytest.raises(ParsingError, match="39790"):
        SearchHtmlParser().parse_listings(card)


@pytest.mark.parametrize(
    "card_url",
    [
        "https://bad host.example/property/listing/",
        "https://user:password@arthusoimoveis.com.br/property/listing/",
        "https://arthusoimoveis.com.br:invalid/property/listing/",
        "https://[invalid]/property/listing/",
        "https://arthusoimoveis.com.br/wp-json/wp/v2/properties/39790",
        "https://arthusoimoveis.com.br/wp-content/uploads/photo.jpg",
        "https://arthusoimoveis.com.br/busca/?status%5B0%5D=alugar",
    ],
)
def test_parse_listings_rejects_invalid_public_listing_urls(card_url: str) -> None:
    """Reject malformed authorities and non-property endpoint URLs."""
    card = SAMPLE_CARD_HTML.replace(
        "https://arthusoimoveis.com.br/property/apartamento-locacao-centro-timoteo/",
        card_url,
    )

    with pytest.raises(ParsingError, match="39790"):
        SearchHtmlParser().parse_listings(card)


@pytest.mark.parametrize(
    "public_base_url",
    [
        "https://bad host.example/",
        "https://user:password@public.example/",
        "https://public.example:invalid/",
        "https://[invalid]/",
    ],
)
def test_parser_rejects_malformed_public_base(public_base_url: str) -> None:
    """Reject malformed origin configuration before parsing listings."""
    with pytest.raises(ValueError, match="public base URL"):
        SearchHtmlParser(public_base_url=public_base_url)


def test_parse_listings_sample() -> None:
    parser = SearchHtmlParser()
    collection = parser.parse_listings(SAMPLE_CARD_HTML)
    assert len(collection) == 1
    item = collection[0]
    assert item.post_id is not None
    assert item.post_id.value == 39790
    assert item.slug == "apartamento-locacao-centro-timoteo"
    assert "Centro Norte" in item.title
    assert item.price_text == "R$ 950,00"
    assert item.bedrooms == 2
    assert item.bathrooms == 1
    assert item.property_type == "Apartamento"
    assert len(item.images) == 2
    assert item.images[0] == "https://arthusoimoveis.com.br/img1.jpeg"


def test_parse_listings_empty_html() -> None:
    parser = SearchHtmlParser()
    collection = parser.parse_listings("")
    assert collection.is_empty()
