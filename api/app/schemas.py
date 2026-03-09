from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from decimal import Decimal
from typing import Optional, List


# CITY SCHEMAS
class CityBase(BaseModel):
    name: str = Field(..., example="Leeds")
    latitude: Decimal = Field(..., max_digits=10, decimal_places=6, example=53.79)
    longitude: Decimal = Field(..., max_digits=10, decimal_places=6, example=1.61)

    @field_validator('name')
    @classmethod
    def force_lowercase(cls, v: str) -> str:
        return v.lower()

class CityCreate(CityBase):
    pass

class CityRead(CityBase):
    id: int = Field(..., example=1)
    model_config = ConfigDict(from_attributes=True)



# STATION SCHEMAS
class StationBase(BaseModel):
    name: str = Field(..., example="Leeds Station")
    city_id: int = Field(..., example=1)

    @field_validator('name')
    @classmethod
    def force_lowercase(cls, v: str) -> str:
        return v.lower()

class StationCreate(StationBase):
    pass

class StationRead(StationBase):
    city: CityRead
    model_config = ConfigDict(from_attributes=True)



# TRANSPORT MODE SCHEMAS
class TransportModeBase(BaseModel):
    name: str = Field(..., example="train")

    @field_validator('name')
    @classmethod
    def force_lowercase(cls, v: str) -> str:
        return v.lower()

class TransportModeCreate(TransportModeBase):
    pass

class TransportModeRead(TransportModeBase):
    id: int = Field(..., example=1)
    model_config = ConfigDict(from_attributes=True)



# ROUTE SCHEMAS
class RouteBase(BaseModel):
    price: Decimal = Field(..., max_digits=10, decimal_places=2, example=12.50)
    notes: Optional[str] = Field(..., example="Northern Rail Service")

# Fields required when CREATING a route (via POST)
class RouteCreate(RouteBase):
    origin_station_id: int 
    destination_station_id: int
    transport_mode_id: int

# Fields returned when READING a route (via GET)
class RouteRead(RouteBase):
    id: int = Field(..., example=1)
    origin_station: StationRead
    destination_station: StationRead
    transport_mode: TransportModeRead
    
    model_config = ConfigDict(from_attributes=True)

# JOURNEY SCHEMAS - This is the result of our Dijkstra. We return the cheapest route
class JourneyRead(BaseModel):
    total_price: Decimal = Field(..., example=12.50)
    ticket_price: Decimal = Field(..., example=12.50)
    railcard_discounts: Decimal = Field(..., example=0.00)
    advanced_discounts: Decimal = Field(..., example=0.00)
    transfer_price: Decimal = Field(..., example=0.00)
    path: List[RouteRead]

    model_config = ConfigDict(from_attributes=True)


# AUTHENTICATION SCHEMAs
class AuthSchema(BaseModel):
    email: EmailStr
    password: str

class SignupResponse(BaseModel):
    message: str
    id: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"