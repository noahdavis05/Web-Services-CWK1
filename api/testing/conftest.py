import pytest 
from fastapi.testclient import TestClient 
from app.main import app 
from unittest.mock import MagicMock
from app.utils.supabase_client import supabase
from app.utils.verify_auth_token import get_current_user
from app.database import engine, get_db
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def client(mock_supabase_auth, mock_graph_manager):
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def mock_supabase_auth(monkeypatch):
    """
    Mock the authentication functions
    """
    mock_auth = MagicMock()

    # mock the sign up function
    mock_signup_response = MagicMock()
    mock_signup_response.user.id = "mock-uuid-123"
    mock_auth.sign_up.return_value = mock_signup_response

    # mock the login function
    mock_login_response = MagicMock()
    mock_login_response.session.access_token = "fake-access-token"
    mock_login_response.session.refresh_token = "fake-refresh-token"
    mock_auth.sign_in_with_password.return_value = mock_login_response

    monkeypatch.setattr(supabase, "auth", mock_auth)
    
    return mock_auth


@pytest.fixture(autouse=True)
def mock_graph_manager(monkeypatch):
    """
    Mocks the graph manager singleton class - therefore we don't download all the routes from db
    """
    mock_gm_instance = MagicMock()

    # create a few mock routes for the tests
    mock_gm_instance.graph = { 
        ## simple mock route from leeds to Bath
        8: [
                {
                "route_id": 1,
                "origin_city_loc": (53, 1.5),
                "destination_city_loc": (51, 2),
                "destination_city":  120,
                "origin_station_id": 224,
                "destination_station_id": 120,
                "price": 100.00,
                "transport_mode_id": 2
            },
            {
                "route_id": 275,
                "origin_city_loc": (53.797500, -1.543600),
                "destination_city_loc": (57.150000, -2.110000), 
                "destination_city": 55,
                "origin_station_id": 3, 
                "destination_station_id": 4,  
                "price": 17.99,
                "transport_mode_id": 1 
            },
            {
                "route_id": 616,
                "origin_city_loc": (53.797500, -1.543600),
                "destination_city_loc": (57.150000, -2.110000), 
                "destination_city": 55,
                "origin_station_id": 3, 
                "destination_station_id": 4,  
                "price": 100,
                "transport_mode_id": 2
            }
        ],
        ## Complex mock route from exeter to aberdeen
        86: [  
            {
                "route_id": 183,
                "origin_city_loc": (50.725600, -3.526900),  
                "destination_city_loc": (51.453600, -2.597500),  
                "destination_city": 5,
                "origin_station_id": 1,  
                "destination_station_id": 2, 
                "price": 5.50,
                "transport_mode_id": 1  
            }
        ],
        5: [ 
            {
                "route_id": 90,
                "origin_city_loc": (51.453600, -2.597500),
                "destination_city_loc": (53.797500, -1.543600), 
                "destination_city": 8,
                "origin_station_id": 2,  
                "destination_station_id": 3, 
                "price": 8.50,
                "transport_mode_id": 1  
            }
        ],
    }
    
    monkeypatch.setattr("app.routers.journeys.GraphManager", lambda: mock_gm_instance)

    return mock_gm_instance

## Mock for verifying authentication for all endpoints
class MockUser:
    id = "user-123"
    email = "user@example.com"
    user_metadata = {"role": "user"}

class MockAdmin:
    id = "admin-456"
    email = "admin@example.com"
    user_metadata = {"role": "admin"}

@pytest.fixture
def as_user():
    """returns the user as a user"""
    app.dependency_overrides[get_current_user] = lambda: MockUser()
    yield
    app.dependency_overrides = {} 

@pytest.fixture
def as_admin():
    """returns the app as an admin"""
    app.dependency_overrides[get_current_user] = lambda: MockAdmin()
    yield
    app.dependency_overrides = {}


# overrides to ensure that any commit is rolled back
# this means our test db always stays the same
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture
def db_session():
    connection = engine.connect()

    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)