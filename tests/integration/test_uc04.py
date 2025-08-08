import pytest
from unittest.mock import patch
from kusibot.database.models import User
from app import bcrypt

@pytest.fixture(scope="function")
def db_uc04(it_db_session):
    """A database session with one registered standard user."""

    standard_user = User(
        username = "test_user",
        email = "test@email.com",
        password = bcrypt.generate_password_hash("Password123!").decode('utf-8')
    )

    it_db_session.add(standard_user)
    it_db_session.commit()

    return it_db_session

# ---- Test for UC04: Log In to the System ----

def test_it10_successful_login_standard(db_uc04, client):
    
    # Action: POST /auth/login with valid data
    response = client.post("/auth/login", data = {
        "identifier": "test_user",
        "password": "Password123!",
        "remember": "False"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 1 # Check that there was one redirect response.
    assert b"KusiChat" in response.data

def test_it11_successful_login_professional(db_uc04, client):
    
    # Action: POST /auth/login with valid data
    response = client.post("/auth/login", data = {
        "identifier": "test_prof_user",
        "password": "professional123",
        "remember": "False"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 1 # Check that there was one redirect response.
    assert b"Dashboard" in response.data

def test_it12_unsuccessful_login_unknown_identifier(db_uc04, client):
    
    # Action: POST /auth/login with an unknown identifier
    response = client.post("/auth/login", data = {
        "identifier": "unknown_user",
        "password": "Password123!",
        "remember": "False"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was one redirect response.
    assert b"Login" in response.data
    assert b"Invalid username or password." in response.data

def test_it13_successful_login_wrong_password(db_uc04, client):
    
    # Action: POST /auth/login with a wrong password
    response = client.post("/auth/login", data = {
        "identifier": "test_user",
        "password": "WRONG_PASSWORD123",
        "remember": "False"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was one redirect response.
    assert b"Login" in response.data
    assert b"Invalid username or password." in response.data

@patch('kusibot.app.auth.routes.auth_service')
def test_it14_successful_login_db_error(mock_auth_service, db_uc04, client):
    
    # Raising a DB Error
    mock_auth_service.possible_login.return_value = None

    # Action: POST /auth/login with valid data
    response = client.post("/auth/login", data = {
        "identifier": "test_user",
        "password": "Password123!",
        "remember": "False"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was one redirect response.
    assert b"Invalid username or password." in response.data