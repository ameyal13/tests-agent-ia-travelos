from apify_client import ApifyClient
from ..config.settings import settings
from ..schemas.output_schema import FlightResult
from typing import List

def search_flights(
    origin: str,
    destination: str,
    date: str,
    adults: int = 1
) -> List[FlightResult]:
    """
    Llama al actor de Apify que scrapeea vuelos.
    Devuelve lista de FlightResult listos para el agente.
    """
    client = ApifyClient(settings.apify_api_token)

    run_input = {
        "origin.0": origin,        # "Guadalajara, MX"
        "target.0": destination,   # "Cancún, MX"
        "depart.0": date,          # "2026-07-10"
        "non_stop": False,
        "one_stop": True,
        "two_stop": True,
        "alternate_origin": False,
        "alternate_target": False,
    }

    run = client.actor(settings.apify_flights_actor_id).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    results = []
    for item in items:
        try:
            results.append(FlightResult(
                airline=item.get("airline", ""),
                flight_number=item.get("flightNumber", ""),
                origin_iata=item.get("originIata", origin),
                destination_iata=item.get("destIata", destination),
                departure_dt=item.get("departureTime", ""),
                arrival_dt=item.get("arrivalTime", ""),
                duration_min=item.get("durationMinutes", 0),
                price_mxn=float(item.get("price", 0)),
                stops=item.get("stops", 0),
                source_url=item.get("url", ""),
            ))
        except Exception as e:
            print(f"[flights] item descartado: {e}")

    return results
