"""Unit tests for ResponseDeserializer."""

from arthuso.infrastructure.deserializer import ResponseDeserializer


def test_deserialize_taxonomy_terms() -> None:
    raw_cities = [
        {"id": 82, "name": "Timóteo", "slug": "timoteo", "count": 346},
        {"id": 41, "name": "Coronel Fabriciano", "slug": "cel-fabriciano", "count": 186},
    ]
    deserializer = ResponseDeserializer()
    collection = deserializer.deserialize_cities(raw_cities)
    assert len(collection) == 2
    assert collection[0].term_id == 82
    assert collection[0].name == "Timóteo"
    assert collection[0].slug == "timoteo"
    assert collection[0].count == 346


def test_deserialize_property_detail() -> None:
    raw_prop = {
        "id": 39823,
        "slug": "casa-santa-maria-timoteo",
        "link": "https://arthusoimoveis.com.br/property/casa-santa-maria-timoteo/",
        "title": {"rendered": "Casa para locação em Santa Maria"},
        "content": {"rendered": "<p>Excelente casa 3 quartos.</p>"},
        "property_meta": {
            "fave_property_price": ["3500"],
            "fave_property_bedrooms": ["3"],
            "fave_property_bathrooms": ["2"],
            "fave_property_id": ["1135"],
        },
        "_embedded": {
            "wp:term": [
                [{"taxonomy": "property_city", "name": "Timóteo"}],
                [{"taxonomy": "property_status", "name": "Alugar"}],
            ]
        },
    }
    deserializer = ResponseDeserializer()
    detail = deserializer.deserialize_property_detail(raw_prop)
    assert detail.summary.post_id is not None
    assert detail.summary.post_id.value == 39823
    assert detail.summary.slug == "casa-santa-maria-timoteo"
    assert detail.summary.property_code == "1135"
    assert detail.summary.bedrooms == 3
    assert detail.summary.bathrooms == 2
    assert "3500" in detail.summary.price_text
    assert "Excelente casa" in detail.description
    assert "property_city" in detail.terms
    assert detail.terms["property_city"] == ["Timóteo"]
