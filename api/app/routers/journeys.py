from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.graph_manager import GraphManager
from ..utils.journey_finder import find_cheapest_path
from ..utils.verify_auth_token import get_current_user

router = APIRouter(
    prefix="/journeys",
    tags=["Journeys"]
)


@router.get(
    "/id", 
    # Notice: 'get_journey' renamed locally in documentation if needed, 
    # but FastAPI will use the function name.
    response_model=schemas.JourneyRead, 
    status_code=200,
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."},
        404: {"description": "Not Found - No journey could be calculated between the provided IDs."}
    }
)
async def get_journey_by_id(origin_id: int, destination_id: int, railcard_discount: int = 0, advanced_fares: bool = False, max_coach_legs: int = 2, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    ### Fetch a journey by city IDs
    Calculates the **cheapest route** between two cities using their unique integer identifiers.
    
    The algorithm evaluates multiple transport modes (Rail, FlixBus, National Express) to find the most cost-effective path.

    **Access Level:** **Admin** and **User**.

    **Notes:**
    - The **total_price** includes a **£3.00 changeover fee** for every station transfer required.
    - Result includes a full breakdown of ticket costs, applied discounts, and individual journey legs.
    """
    
    graph_manager = GraphManager() # gets us our instance of our singleton class
    

    cheapest_path = await find_cheapest_path(graph_manager, origin_id, destination_id, railcard_discount, advanced_fares, max_coach_legs)
    if not cheapest_path:
        raise HTTPException(status_code=404, detail="No journey found")
    
    # now need to get all the paths from the db in order
    all_routes = []
    for route_id in cheapest_path["route_ids"]:
        route = db.query(models.Route).filter(models.Route.id == route_id).first()
        all_routes.append(route)

    return {
        "total_price": cheapest_path['ticket_costs'] - cheapest_path['ticket_discounts'] - cheapest_path["advanced_discounts"] + cheapest_path['extra_costs'],
        "ticket_price": cheapest_path['ticket_costs'],
        "railcard_discounts": cheapest_path['ticket_discounts'],
        "advanced_discounts": cheapest_path['advanced_discounts'],
        "transfer_price": cheapest_path["extra_costs"],
        "path": all_routes
    }


@router.get(
    "/name", 
    response_model=schemas.JourneyRead, 
    status_code=200,
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."},
        404: {"description": "Not Found - One or both city names do not exist, or no path was found."}
    }
)
async def get_journey_by_name(origin_name: str, destination_name: str, railcard_discount: int = 0, advanced_fares: bool = False, max_coach_legs: int = 2, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    ### Fetch a journey by city names
    Calculates the **cheapest route** between two cities using their string names.
    
    

    **Access Level:** **Admin** and **User**.

    **Notes:**
    - City names are **case-insensitive**.
    - The calculation accounts for **railcard discounts** and **advanced fare** estimates if enabled.
    - A **£3.00 transfer fee** is added to the total price for each leg transition.
    """

    # get both the origin and destination IDs from the names
    origin_city = db.query(models.City).filter(models.City.name == origin_name.lower()).first()
    destination_city = db.query(models.City).filter(models.City.name == destination_name.lower()).first()

    if not origin_city:
        raise HTTPException(status_code=404, detail=f"No city {origin_name} found.")
    if not destination_city:
        raise HTTPException(status_code=404, detail=f"No city {destination_name} found.")
    
    origin_id = origin_city.id
    destination_id = destination_city.id

    
    graph_manager = GraphManager() # gets us our instance of our singleton class
    

    cheapest_path = await find_cheapest_path(graph_manager, origin_id, destination_id, railcard_discount, advanced_fares, max_coach_legs)
    if not cheapest_path:
        raise HTTPException(status_code=404, detail="No journey found")


    # now need to get all the paths from the db in order
    all_routes = []
    for route_id in cheapest_path["route_ids"]:
        route = db.query(models.Route).filter(models.Route.id == route_id).first()
        all_routes.append(route)

    return {
        "total_price": cheapest_path['ticket_costs'] - cheapest_path['ticket_discounts'] - cheapest_path["advanced_discounts"] + cheapest_path['extra_costs'],
        "ticket_price": cheapest_path['ticket_costs'],
        "railcard_discounts": cheapest_path['ticket_discounts'],
        "advanced_discounts": cheapest_path['advanced_discounts'],
        "transfer_price": cheapest_path["extra_costs"],
        "path": all_routes
    }