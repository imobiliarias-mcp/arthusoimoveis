"""Script executing live reverse-engineered rental research against Arthuso Imóveis."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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


def main() -> int:
    """Executes live research verification pipeline."""
    print("=" * 70)
    print("Arthuso Imóveis - Live Rental Search Research & Verification")
    print("=" * 70)

    transport = HttpxTransport()
    deserializer = ResponseDeserializer()
    service = RentalResearchService(transport, deserializer)
    url_parser = FrontendUrlParser()

    print(f"\n[1] Deconstructing Target Research URL:\n    {TARGET_URL}")
    criteria, pagination = url_parser.parse_url(TARGET_URL)
    city_str = criteria.city.as_string() if criteria.city else "None"
    beds_str = criteria.bedrooms.as_string() if criteria.bedrooms else "None"
    print(f"    - City: {city_str}")
    print(f"    - Bedrooms: {beds_str}")
    print(f"    - Page: {pagination.page.as_string()}")

    print("\n[2] Executing Target Rental Search via Service...")
    properties = service.search_by_url(TARGET_URL)
    print(f"    -> Results found: {len(properties)} properties")

    for idx, prop in enumerate(properties, 1):
        post_id_val = prop.post_id.value if prop.post_id else "N/A"
        print(f"\n    Property #{idx} (Post ID: {post_id_val}):")
        print(f"      Title: {prop.title}")
        print(f"      Price: {prop.price_text}")
        print(f"      Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}")
        print(f"      Type: {prop.property_type}")
        print(f"      Gallery Images: {len(prop.images)} embedded photos")
        print(f"      Link: {prop.url or prop.detail_url}")

    print("\n[3] Discovering Filter Taxonomies...")
    cities = service.get_cities()
    print(f"    -> Cities available: {len(cities)} cities found")
    for city in list(cities)[:5]:
        print(f"       - {city.name} (Slug: {city.slug}, Count: {city.count})")

    neighborhoods = service.get_neighborhoods()
    print(f"    -> Neighborhoods available: {len(neighborhoods)} areas found")
    for area in list(neighborhoods)[:5]:
        print(f"       - {area.name} (Slug: {area.slug}, Count: {area.count})")

    types = service.get_property_types()
    print(f"    -> Property types: {len(types)} types found")
    for ptype in list(types)[:5]:
        print(f"       - {ptype.name} (Slug: {ptype.slug}, Count: {ptype.count})")

    if not properties.is_empty() and properties[0].post_id:
        sample_post_id = properties[0].post_id
        print(f"\n[4] Retrieving Rich Details for Post ID {sample_post_id.value}...")
        details = service.get_property_by_id(sample_post_id)
        code = details.summary.property_code or "N/A"
        print(f"    -> Reference Code: {code}")
        print(f"    -> Description length: {len(details.description)} characters")
        print(f"    -> Embedded taxonomies: {list(details.terms.keys())}")
        for tax, terms in details.terms.items():
            print(f"       * {tax}: {terms}")

    print("\n" + "=" * 70)
    print("Verification Completed Successfully: All endpoints reproduced.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
