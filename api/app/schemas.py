from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional

# CITY SCHEMAS
class CityBase(BaseModel):
    name: str 
    latitude: Decimal = Field(..., max_digits=10, decimal_places=6)
    longitude: Decimal = Field(..., max_digits=10, decimal_places=6)

class CityCreate(CityBase):
    pass

class CityRead(CityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)



# STATION SCHEMAS
class StationBase(BaseModel):
    name: str 
    city_id: int 

class StationCreate(StationBase):
    pass

class StationRead(StationBase):
    id: int 
    name: str 
    city: CityRead
    model_config = ConfigDict(from_attributes=True)



# ROUTE SCHEMAS
class RouteBase(BaseModel):
    travel_mode: str
    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    notes: Optional[str] = None

# Fields required when CREATING a route (via POST)
class RouteCreate(RouteBase):
    origin_station_id: int 
    destination_station_id: int

# Fields returned when READING a route (via GET)
class RouteRead(RouteBase):
    id: int
    origin_station: StationRead
    destination_station: StationRead
    
    model_config = ConfigDict(from_attributes=True)