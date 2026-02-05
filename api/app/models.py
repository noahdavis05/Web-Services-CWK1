from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from .database import Base

"""
Database model class for a route between two cities.
Contains start city, end city, travel mode (e.g. train or coach), price, and extra notes
"""
class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    origin_city = Column(String, nullable=False)
    destination_city = Column(String, nullable=False)
    travel_mode = Column(String, nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    notes = Column(String, nullable=True)