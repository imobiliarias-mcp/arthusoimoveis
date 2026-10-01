"""Unit tests for domain primitive value objects."""

import pytest
from arthuso.domain.exceptions import ValidationError
from arthuso.domain.primitives import (
    PropertyId,
    PropertyCode,
    RentalPrice,
    CitySlug,
    NeighborhoodSlug,
    PropertyTypeSlug,
    BedroomCount,
    BathroomCount,
    PageNumber,
    SortOrder,
)


def test_property_id_valid() -> None:
    pid = PropertyId(39790)
    assert pid.value == 39790
    assert pid.as_string() == "39790"


def test_property_id_invalid() -> None:
    with pytest.raises(ValidationError):
        PropertyId(0)
    with pytest.raises(ValidationError):
        PropertyId(-5)


def test_property_code_valid() -> None:
    code = PropertyCode(" 1134 ")
    assert code.value == " 1134 "
    assert code.as_string() == "1134"


def test_property_code_invalid() -> None:
    with pytest.raises(ValidationError):
        PropertyCode("   ")


def test_rental_price_valid() -> None:
    price = RentalPrice(1250.50)
    assert price.amount == 1250.50
    assert price.as_integer_string() == "1250"


def test_rental_price_invalid() -> None:
    with pytest.raises(ValidationError):
        RentalPrice(-1.0)


def test_city_slug_valid() -> None:
    slug = CitySlug(" Timoteo ")
    assert slug.as_string() == "timoteo"


def test_city_slug_invalid() -> None:
    with pytest.raises(ValidationError):
        CitySlug("")


def test_neighborhood_slug_valid() -> None:
    slug = NeighborhoodSlug(" Centro ")
    assert slug.as_string() == "centro"


def test_neighborhood_slug_invalid() -> None:
    with pytest.raises(ValidationError):
        NeighborhoodSlug("")


def test_property_type_slug_valid() -> None:
    slug = PropertyTypeSlug(" Apartamento ")
    assert slug.as_string() == "apartamento"


def test_bedroom_count_valid() -> None:
    count = BedroomCount(2)
    assert count.count == 2
    assert count.as_string() == "2"


def test_bedroom_count_invalid() -> None:
    with pytest.raises(ValidationError):
        BedroomCount(-1)


def test_bathroom_count_valid() -> None:
    count = BathroomCount(1)
    assert count.count == 1
    assert count.as_string() == "1"


def test_page_number_valid() -> None:
    page = PageNumber(1)
    assert page.value == 1
    assert page.as_string() == "1"


def test_page_number_invalid() -> None:
    with pytest.raises(ValidationError):
        PageNumber(0)


def test_sort_order_valid() -> None:
    order = SortOrder("a_price")
    assert order.as_string() == "a_price"


def test_sort_order_invalid() -> None:
    with pytest.raises(ValidationError):
        SortOrder("invalid_sort")
