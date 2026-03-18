from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Travelers(BaseModel):
    adults: int = Field(ge=1)
    children: int = Field(default=0, ge=0)


class Preferences(BaseModel):
    hotel_stars: Optional[int] = Field(default=3, ge=1, le=5)
    hotel_type: Optional[str] = "any"  # all-inclusive, boutique, etc.
    flight_class: Optional[str] = "economy"
    extras: Optional[List[str]] = []  # traslado, seguro, tours…


class TripRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    departure_date: date
    return_date: date
    travelers: Travelers
    budget_mxn: float = Field(gt=0)
    preferences: Optional[Preferences] = Preferences()
    notes: Optional[str] = ""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import uuid

class Travelers(BaseModel):
    adults: int = Field(ge=1)
    children: int = Field(default=0, ge=0)

class Preferences(BaseModel):
    hotel_stars: Optional[int] = Field(default=3, ge=1, le=5)
    hotel_type: Optional[str] = "any"           # all-inclusive, boutique, etc.
    flight_class: Optional[str] = "economy"
    extras: Optional[List[str]] = []          # traslado, seguro, tours…

class TripRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str                                # "Guadalajara, MX"
    destination: str                           # "Cancún, MX"
    departure_date: date
    return_date: date
    travelers: Travelers
    budget_mxn: float = Field(gt=0)
    preferences: Optional[Preferences] = Preferences()

    # aquí puedes agregar más campos que quieras sin romper nada
    notes: Optional[str] = ""
