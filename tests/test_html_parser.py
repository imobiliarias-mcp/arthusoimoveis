"""Unit tests for SearchHtmlParser."""

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
