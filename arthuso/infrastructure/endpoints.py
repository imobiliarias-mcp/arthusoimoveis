"""Endpoints and HTTP constants for Arthuso Imóveis."""

from typing import Dict

BASE_URL: str = "https://arthusoimoveis.com.br"
SEARCH_PATH: str = "/busca/"
PROPERTIES_PATH: str = "/wp-json/wp/v2/properties"
PROPERTY_STATUS_PATH: str = "/wp-json/wp/v2/property_status"
PROPERTY_CITY_PATH: str = "/wp-json/wp/v2/property_city"
PROPERTY_AREA_PATH: str = "/wp-json/wp/v2/property_area"
PROPERTY_TYPE_PATH: str = "/wp-json/wp/v2/property_type"
MEDIA_PATH: str = "/wp-json/wp/v2/media"
ADMIN_AJAX_PATH: str = "/wp-admin/admin-ajax.php"

PAGE_SIZE: int = 9

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8,application/json"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}
