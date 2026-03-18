import json
from langchain_openai import ChatOpenAI
from ..config.settings import settings
from .apify_flights import search_flights
from .prompts import FLIGHTS_SYSTEM_PROMPT, FLIGHTS_USER_TEMPLATE
from ..schemas.output_schema import FlightResult, FlightPair
from typing import Optional

llm = ChatOpenAI(
    model=settings.model_name,
    api_key=settings.nvidia_api_key,
    base_url=settings.nvidia_base_url,
    temperature=settings.temperature,
)

def run_flights_agent(state: dict) -> dict:
    """
    Recibe el estado del grafo LangGraph.
    Busca vuelos ida y vuelta, le pasa los resultados al LLM
    y devuelve el estado actualizado con los vuelos seleccionados.
    """
    req = state["request"]

    # 1. Llamar a Apify para ida y vuelta
    outbound_raw = search_flights(
        origin=req.origin,
        destination=req.destination,
        date=str(req.departure_date),
        adults=req.travelers.adults,
    )
    return_raw = search_flights(
        origin=req.destination,
        destination=req.origin,
        date=str(req.return_date),
        adults=req.travelers.adults,
    )

    # 2. Serializar resultados para el prompt
    outbound_json = json.dumps([f.model_dump() for f in outbound_raw], ensure_ascii=False)
    return_json   = json.dumps([f.model_dump() for f in return_raw],   ensure_ascii=False)

    # 3. Armar el prompt
    user_msg = FLIGHTS_USER_TEMPLATE.format(
        origin=req.origin,
        destination=req.destination,
        departure_date=req.departure_date,
        return_date=req.return_date,
        adults=req.travelers.adults,
        children=req.travelers.children,
        budget_mxn=req.budget_mxn,
        flight_class=req.preferences.flight_class,
        outbound_flights_json=outbound_json,
        return_flights_json=return_json,
    )

    # 4. Llamar al LLM
    messages = [
        {"role": "system", "content": FLIGHTS_SYSTEM_PROMPT},
        {"role": "user",   "content": user_msg},
    ]
    response = llm.invoke(messages)

    # 5. Parsear respuesta JSON
    try:
        data = json.loads(response.content)
        flight_pair = FlightPair(
            outbound=FlightResult(**data["outbound"]) if data.get("outbound") else None,
            returning=FlightResult(**data["return"])  if data.get("return")   else None,
        )
    except Exception as e:
        print(f"[flight_agent] error parseando respuesta: {e}")
        flight_pair = FlightPair()

    # 6. Actualizar estado del grafo
    state["flights"] = flight_pair
    state["errors"] = state.get("errors", [])
    return state