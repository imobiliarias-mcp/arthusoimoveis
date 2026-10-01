"""Unit tests for SearchQueryBuilder."""

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
from arthuso.infrastructure.query_builder import SearchQueryBuilder


def test_build_path_default_page() -> None:
    builder = SearchQueryBuilder()
    path = builder.build_path(PaginationSpec(page=PageNumber(1)))
    assert path == "/busca/"


def test_build_path_page_two() -> None:
    builder = SearchQueryBuilder()
    path = builder.build_path(PaginationSpec(page=PageNumber(2)))
    assert path == "/busca/page/2/"


def test_build_parameters_empty_criteria() -> None:
    builder = SearchQueryBuilder()
    params = builder.build_parameters(SearchCriteria())
    assert params == {"status[0]": "alugar"}


def test_build_parameters_full_criteria() -> None:
    builder = SearchQueryBuilder()
    criteria = SearchCriteria(
        city=CitySlug("timoteo"),
        neighborhood=NeighborhoodSlug("centro"),
        property_type=PropertyTypeSlug("apartamento"),
        bedrooms=BedroomCount(2),
        bathrooms=BathroomCount(1),
        min_price=RentalPrice(800.0),
        max_price=RentalPrice(2000.0),
        property_code=PropertyCode("1134"),
        keyword="norte",
        sort_by=SortOrder("a_price"),
    )
    params = builder.build_parameters(criteria)
    assert params["status[0]"] == "alugar"
    assert params["location[0]"] == "timoteo"
    assert params["areas[0]"] == "centro"
    assert params["type[0]"] == "apartamento"
    assert params["bedrooms"] == "2"
    assert params["bathrooms"] == "1"
    assert params["min-price"] == "800"
    assert params["max-price"] == "2000"
    assert params["property_id"] == "1134"
    assert params["keyword"] == "norte"
    assert params["sortby"] == "a_price"
