import time
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict, Any

from ..schemas.input_schema import TripRequest
from ..schemas.output_schema import TripResponse, FlightPair, HotelResult, Package, Metadata
from ..flights.flight_agents import run_flights_agent
from ..hotels.hotel_agent import run_hotels_agent
from ..packager.packager_agent import run_packager_agent


# ── Estado que viaja entre nodos del grafo ──────────────────────
class TripState(TypedDict):
    request:  TripRequest
    flights:  Optional[FlightPair]
    hotels:   Optional[List[HotelResult]]
    packages: Optional[Dict[str, Package]]
    errors:   List[str]
    start_ms: int


# ── Nodos ────────────────────────────────────────────────────────
def node_flights(state: TripState) -> TripState:
    try:
        return run_flights_agent(state)
    except Exception as e:
        state["errors"].append(f"flights: {str(e)}")
        return state

def node_hotels(state: TripState) -> TripState:
    try:
        return run_hotels_agent(state)
    except Exception as e:
        state["errors"].append(f"hotels: {str(e)}")
        return state

def node_packager(state: TripState) -> TripState:
    try:
        return run_packager_agent(state)
    except Exception as e:
        state["errors"].append(f"packager: {str(e)}")
        return state


# ── Construcción del grafo ───────────────────────────────────────
def build_graph():
    graph = StateGraph(TripState)

    graph.add_node("flights",  node_flights)
    graph.add_node("hotels",   node_hotels)
    graph.add_node("packager", node_packager)

    # vuelos y hoteles corren en paralelo → luego el armador
    graph.set_entry_point("flights")
    graph.add_edge("flights",  "hotels")
    graph.add_edge("hotels",   "packager")
    graph.add_edge("packager", END)

    return graph.compile()


trip_graph = build_graph()


# ── Función pública que llama main_agents.py ─────────────────────
def run_trip(request: TripRequest) -> TripResponse:
    start = int(time.time() * 1000)

    initial_state: TripState = {
        "request":  request,
        "flights":  None,
        "hotels":   [],
        "packages": {},
        "errors":   [],
        "start_ms": start,
    }

    final_state = trip_graph.invoke(initial_state)

    elapsed = int(time.time() * 1000) - start
    errors  = final_state.get("errors", [])

    return TripResponse(
        request_id=request.request_id,
        status="success" if not errors else "partial",
        flights=final_state.get("flights"),
        hotels=final_state.get("hotels", []),
        packages=final_state.get("packages", {}),
        metadata=Metadata(
            processing_ms=elapsed,
            agents_used=["flights", "hotels", "packager"],
            errors=errors,
        ),
    )