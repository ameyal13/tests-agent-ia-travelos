import json
from langchain_openai import ChatOpenAI
from ..config.settings import settings
from .prompts import PACKAGER_SYSTEM_PROMPT, PACKAGER_USER_TEMPLATE
from ..schemas.output_schema import Package, FlightPair, HotelResult

llm = ChatOpenAI(
    model=settings.model_name,
    api_key=settings.nvidia_api_key,
    base_url=settings.nvidia_base_url,
    temperature=settings.temperature,
)

def run_packager_agent(state: dict) -> dict:
    req      = state["request"]
    flights  = state.get("flights")
    hotels   = state.get("hotels", [])

    flights_json = json.dumps(
        flights.model_dump() if flights else {}, ensure_ascii=False
    )
    hotels_json = json.dumps(
        [h.model_dump() for h in hotels], ensure_ascii=False
    )

    user_msg = PACKAGER_USER_TEMPLATE.format(
        origin=req.origin,
        destination=req.destination,
        departure_date=req.departure_date,
        return_date=req.return_date,
        adults=req.travelers.adults,
        children=req.travelers.children,
        budget_mxn=req.budget_mxn,
        extras=req.preferences.extras,
        flights_json=flights_json,
        hotels_json=hotels_json,
    )

    messages = [
        {"role": "system", "content": PACKAGER_SYSTEM_PROMPT},
        {"role": "user",   "content": user_msg},
    ]
    response = llm.invoke(messages)

    try:
        data = json.loads(response.content)
        packages = {}
        for tier in ["economico", "estandar", "premium"]:
            if tier in data:
                raw = data[tier]
                packages[tier] = Package(
                    tier=tier,
                    flight=FlightPair(**raw["flight"]) if raw.get("flight") else None,
                    hotel=HotelResult(**raw["hotel"])  if raw.get("hotel")  else None,
                    extras=raw.get("extras", []),
                    total_mxn=raw.get("total_mxn", 0.0),
                    savings_mxn=raw.get("savings_mxn", 0.0),
                    summary=raw.get("summary", ""),
                )
    except Exception as e:
        print(f"[packager_agent] error parseando respuesta: {e}")
        packages = {}

    state["packages"] = packages
    return state