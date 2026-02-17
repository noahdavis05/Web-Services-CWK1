import pytest 
from fastapi.testclient import TestClient 
from app.main import app 
from unittest.mock import MagicMock
from app.utils.supabase_client import supabase
from app.utils.verify_auth_token import get_current_user

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
    
    monkeypatch.setattr("app.main.GraphManager", lambda: mock_gm_instance)
    
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