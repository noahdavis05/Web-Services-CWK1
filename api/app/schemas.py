from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional

# Common fields shared by everything
class RouteBase(BaseModel):
    origin_city: str
    destination_city: str
    travel_mode: str
    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    notes: Optional[str] = None

# Fields required when CREATING a route (via POST)
class RouteCreate(RouteBase):
    pass

# Fields returned when READING a route (via GET)
class RouteRead(RouteBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)