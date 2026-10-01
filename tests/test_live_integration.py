"""Live integration tests against arthusoimoveis.com.br."""

import pytest
from arthuso import (
    HttpxTransport,
    ResponseDeserializer,
    RentalResearchService,
    FrontendUrlParser,
    PropertyId,
)

TARGET_URL = (
    "https://arthusoimoveis.com.br/busca/"
    "?status%5B%5D=alugar&property_id=&keyword="
    "&location%5B%5D=timoteo&areas%5B%5D=&bedrooms=2&max-price="
)


@pytest.fixture
def service() -> RentalResearchService:
    transport = HttpxTransport()
    deserializer = ResponseDeserializer()
    return RentalResearchService(transport, deserializer)


def test_live_search_target_url(service: RentalResearchService) -> None:
    properties = service.search_by_url(TARGET_URL)
    assert len(properties) >= 1
    first_prop = properties[0]
    assert first_prop.post_id is not None
    assert first_prop.post_id.value > 0
    assert first_prop.slug != ""
    assert "R$" in first_prop.price_text
    assert first_prop.bedrooms == 2


def test_live_pagination(service: RentalResearchService) -> None:
    parser = FrontendUrlParser()
    criteria, pagination = parser.parse_url(
        "https://arthusoimoveis.com.br/busca/page/2/?status[0]=alugar&location[0]=timoteo"
    )
    assert pagination.page.value == 2
    properties = service.search_rentals(criteria, pagination)
    assert len(properties) > 0


def test_live_filter_catalogs(service: RentalResearchService) -> None:
    cities = service.get_cities()
    assert len(cities) >= 10
    city_slugs = [c.slug for c in cities]
    assert "timoteo" in city_slugs

    neighborhoods = service.get_neighborhoods()
    assert len(neighborhoods) >= 20

    types = service.get_property_types()
    assert len(types) >= 5
    type_slugs = [t.slug for t in types]
    assert "apartamento" in type_slugs


def test_live_property_detail(service: RentalResearchService) -> None:
    # Post ID 39790 is a known Timóteo 2-bedroom rental
    detail = service.get_property_by_id(PropertyId(39790))
    assert detail.summary.post_id is not None
    assert detail.summary.post_id.value == 39790
    assert detail.summary.slug == "apartamento-disponivel-para-locacao-no-centro-norte-timoteo"
    assert "Centro Norte" in detail.summary.title
    assert detail.summary.bedrooms == 2
