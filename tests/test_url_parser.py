"""Unit tests for FrontendUrlParser."""

from arthuso.application.url_parser import FrontendUrlParser

TARGET_URL = (
    "https://arthusoimoveis.com.br/busca/"
    "?status%5B%5D=alugar&property_id=&keyword="
    "&location%5B%5D=timoteo&areas%5B%5D=&bedrooms=2&max-price="
)


def test_parse_target_url() -> None:
    parser = FrontendUrlParser()
    criteria, pagination = parser.parse_url(TARGET_URL)
    assert criteria.city is not None
    assert criteria.city.as_string() == "timoteo"
    assert criteria.bedrooms is not None
    assert criteria.bedrooms.count == 2
    assert pagination.page.value == 1
    assert criteria.max_price is None
    assert criteria.property_code is None


def test_parse_paginated_url() -> None:
    paginated_url = (
        "https://arthusoimoveis.com.br/busca/page/3/"
        "?status%5B0%5D=alugar&location%5B0%5D=timoteo"
    )
    parser = FrontendUrlParser()
    criteria, pagination = parser.parse_url(paginated_url)
    assert criteria.city is not None
    assert criteria.city.as_string() == "timoteo"
    assert pagination.page.value == 3


def test_parse_full_parameters() -> None:
    full_url = (
        "https://arthusoimoveis.com.br/busca/"
        "?status=alugar&location=timoteo&areas=centro&type=apartamento"
        "&bedrooms=3&bathrooms=2&min-price=1000&max-price=3000"
        "&property_id=1134&keyword=norte&sortby=a_price"
    )
    parser = FrontendUrlParser()
    criteria, pagination = parser.parse_url(full_url)
    assert criteria.city is not None and criteria.city.as_string() == "timoteo"
    assert criteria.neighborhood is not None and criteria.neighborhood.as_string() == "centro"
    assert criteria.property_type is not None and criteria.property_type.as_string() == "apartamento"
    assert criteria.bedrooms is not None and criteria.bedrooms.count == 3
    assert criteria.bathrooms is not None and criteria.bathrooms.count == 2
    assert criteria.min_price is not None and criteria.min_price.amount == 1000.0
    assert criteria.max_price is not None and criteria.max_price.amount == 3000.0
    assert criteria.property_code is not None and criteria.property_code.as_string() == "1134"
    assert criteria.keyword == "norte"
    assert criteria.sort_by is not None and criteria.sort_by.as_string() == "a_price"
    assert pagination.page.value == 1
