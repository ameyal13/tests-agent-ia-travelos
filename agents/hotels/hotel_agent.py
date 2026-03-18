import json
from functools import lru_cache
from langchain_openai import ChatOpenAI
from ..config.settings import settings
from .apify_hotels import search_hotels
from .prompts import HOTELS_SYSTEM_PROMPT, HOTELS_USER_TEMPLATE
from ..schemas.output_schema import HotelResult
from typing import List


@lru_cache(maxsize=1)
def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        temperature=settings.temperature,
    )

def run_hotels_agent(state: dict) -> dict:
    req = state["request"]

    nights = (req.return_date - req.departure_date).days

    raw_hotels = search_hotels(
        destination=req.destination,
        check_in=str(req.departure_date),
        check_out=str(req.return_date),
        adults=req.travelers.adults,
        children=req.travelers.children,
    )

    hotels_json = json.dumps([h.model_dump() for h in raw_hotels], ensure_ascii=False)

    user_msg = HOTELS_USER_TEMPLATE.format(
        destination=req.destination,
        check_in=req.departure_date,
        check_out=req.return_date,
        nights=nights,
        adults=req.travelers.adults,
        children=req.travelers.children,
        budget_mxn=req.budget_mxn,
        hotel_stars=req.preferences.hotel_stars,
        hotel_type=req.preferences.hotel_type,
        hotels_json=hotels_json,
    )

    messages = [
        {"role": "system", "content": HOTELS_SYSTEM_PROMPT},
        {"role": "user",   "content": user_msg},
    ]
    response = _get_llm().invoke(messages)

    try:
        data = json.loads(response.content)
        hotels = [HotelResult(**h) for h in data.get("hotels", [])]
    except Exception as e:
        print(f"[hotel_agent] error parseando respuesta: {e}")
        hotels = []

    state["hotels"] = hotels
    return state