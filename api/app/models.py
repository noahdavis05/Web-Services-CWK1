from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

"""
Database model class for a route between two stations.
Stations belong to a city.
"""
class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Numeric(10,2), nullable=False)
    notes = Column(String, nullable=True)

    # foreign keys
    origin_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    destination_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    transport_mode_id = Column(Integer, ForeignKey("transport_modes.id"), nullable=False)

    # relationships
    origin_station = relationship("Station", foreign_keys=[origin_station_id], back_populates="routes_starting")
    destination_station = relationship("Station", foreign_keys=[destination_station_id], back_populates="routes_ending")
    transport_mode = relationship("TransportMode", back_populates="routes")

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # foreign keys
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)

    # relationships
    city = relationship("City", foreign_keys=[city_id], back_populates="stations")
    routes_starting = relationship("Route", foreign_keys="[Route.origin_station_id]", back_populates="origin_station")
    routes_ending = relationship("Route", foreign_keys="[Route.destination_station_id]", back_populates="destination_station")

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Numeric(10, 6), nullable=False)
    longitude = Column(Numeric(10, 6), nullable=False)

    stations = relationship("Station", back_populates="city")

class TransportMode(Base):
    __tablename__ = "transport_modes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    routes = relationship("Route", back_populates="transport_mode")