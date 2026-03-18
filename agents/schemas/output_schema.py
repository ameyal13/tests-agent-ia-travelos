from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FlightResult(BaseModel):
    airline: str
    flight_number: Optional[str] = ""
    origin_iata: str
    destination_iata: str
    departure_dt: str
    arrival_dt: str
    duration_min: Optional[int] = 0
    price_mxn: float
    stops: int = 0
    source_url: Optional[str] = ""


class FlightPair(BaseModel):
    outbound: Optional[FlightResult] = None
    returning: Optional[FlightResult] = None


class HotelResult(BaseModel):
    name: str
    stars: Optional[int] = 0
    hotel_type: Optional[str] = ""
    check_in: str
    check_out: str
    nights: int
    price_per_night_mxn: float
    total_mxn: float
    rating: Optional[float] = 0.0
    source_url: Optional[str] = ""


class Package(BaseModel):
    tier: str  # economico | estandar | premium
    flight: Optional[FlightPair] = None
    hotel: Optional[HotelResult] = None
    extras: List[str] = []
    total_mxn: float
    savings_mxn: float = 0.0
    summary: str
    custom_fields: Dict[str, Any] = {}


class Metadata(BaseModel):
    processing_ms: int
    agents_used: List[str]
    errors: List[str] = []


class TripResponse(BaseModel):
    request_id: str
    status: str  # success | partial | error
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    flights: Optional[FlightPair] = None
    hotels: Optional[List[HotelResult]] = []
    packages: Optional[Dict[str, Package]] = {}
    metadata: Optional[Metadata] = None
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class FlightResult(BaseModel):
    airline: str
    flight_number: Optional[str] = ""
    origin_iata: str
    destination_iata: str
    departure_dt: str
    arrival_dt: str
    duration_min: Optional[int] = 0
    price_mxn: float
    stops: int = 0
    source_url: Optional[str] = ""

class FlightPair(BaseModel):
    outbound: Optional[FlightResult] = None
    returning: Optional[FlightResult] = None

class HotelResult(BaseModel):
    name: str
    stars: Optional[int] = 0
    hotel_type: Optional[str] = ""
    check_in: str
    check_out: str
    nights: int
    price_per_night_mxn: float
    total_mxn: float
    rating: Optional[float] = 0.0
    source_url: Optional[str] = ""

class Package(BaseModel):
    tier: str                                  # economico | estandar | premium
    flight: Optional[FlightPair] = None
    hotel: Optional[HotelResult] = None
    extras: List[str] = []
    total_mxn: float
    savings_mxn: float = 0.0
    summary: str                               # texto generado por el agente armador
    custom_fields: Dict[str, Any] = {}        # aquí metes lo que quieras extra

class Metadata(BaseModel):
    processing_ms: int
    agents_used: List[str]
    errors: List[str] = []

class TripResponse(BaseModel):
    request_id: str
    status: str                                # success | partial | error
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    flights: Optional[FlightPair] = None
    hotels: Optional[List[HotelResult]] = []
    packages: Optional[Dict[str, Package]] = {}
    metadata: Optional[Metadata] = None
