from fastapi import FastAPI, HTTPException
from .schemas.input_schema import TripRequest
from .schemas.output_schema import TripResponse
from .orchestrator.orchestrator import run_trip


app = FastAPI(
    title="TravelOS — Agentes IA",
    description="Endpoint para búsqueda y armado de paquetes de viaje",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/trip", response_model=TripResponse)
def create_trip(request: TripRequest) -> TripResponse:
    try:
        result = run_trip(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))