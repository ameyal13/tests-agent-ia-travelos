from apify_client import ApifyClient
from ..config.settings import settings
from ..schemas.output_schema import HotelResult
from typing import List


def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    children: int = 0,
) -> List[HotelResult]:

    client = ApifyClient(settings.apify_api_token)

    # ── CAMBIA ESTE BLOQUE cuando pruebes el actor de Booking ──
    run_input = {
        "search": destination,
        "maxItems": 10,
        "currency": "USD",
        "language": "en-gb",
        "sortBy": "distance_from_search",
        "starsCountFilter": "any",
        "minMaxPrice": "0-999999",
        "checkIn": check_in,        # "2026-07-10"
        "checkOut": check_out,      # "2026-07-15"
        "rooms": 1,
        "adults": adults,
        "children": children,
        "extractAdditionalHotelData": False,
    }
    run   = client.actor(settings.apify_hotels_actor_id).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    nights = (
        __import__("datetime").date.fromisoformat(check_out) -
        __import__("datetime").date.fromisoformat(check_in)
    ).days

    results = []
    for item in items:
        try:
            price_per_night = float(item.get("price", 0))
            results.append(HotelResult(
                name=item.get("name", ""),
                stars=item.get("stars", 0),
                hotel_type=item.get("type", ""),
                check_in=check_in,
                check_out=check_out,
                nights=nights,
                price_per_night_mxn=price_per_night,
                total_mxn=price_per_night * nights,
                rating=float(item.get("rating", 0)),
                source_url=item.get("url", ""),
            ))
        except Exception as e:
            print(f"[hotels] item descartado: {e}")

    return results