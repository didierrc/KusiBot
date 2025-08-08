from unittest.mock import patch
from kusibot.database.models import User

# ---- Test for UC03: Register ----

def test_it04_successful_registration(it_db_session, client):

    # Action: POST /auth/signup with valid and unique data
    response = client.post("/auth/signup", data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 1 # Check that there was one redirect response.
    assert b"Registration successful" in response.data
    assert b"Login" in response.data

    user = it_db_session.query(User).filter_by(email="test@example.com").first()
    assert user is not None
    assert user.username == "testuser"

def test_it05_unsuccessful_registration_duplicated_username(it_db_session, client):
    
    # Setup database initial data
    it_db_session.add(User(username = "testuser",
                           email = "test@example.com",
                           password = "password"))
    it_db_session.commit()

    # Action: POST /auth/signup with duplicated username
    response = client.post("/auth/signup", data = {
        "username": "testuser",
        "email": "diff_email@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was NO redirect.
    assert b"That username is already taken" in response.data

    user = it_db_session.query(User).filter_by(email="diff_email@example.com").first()
    assert user is None

def test_it06_unsuccessful_registration_invalid_email(it_db_session, client):
    
    # Action: POST /auth/signup with an invalid email
    response = client.post("/auth/signup", data = {
        "username": "testuser",
        "email": "an_invalid_email.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was NO redirect.
    assert b"Invalid email" in response.data

    user = it_db_session.query(User).filter_by(username="testuser").first()
    assert user is None

def test_it07_unsuccessful_registration_invalid_password(it_db_session, client):
    
    # Action: POST /auth/signup with an invalid password
    response = client.post("/auth/signup", data = {
        "username": "testuser",
        "email": "test@email.com",
        "password": "non_compliant_password",
        "confirm_password": "non_compliant_password"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was NO redirect.
    assert b"Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character." in response.data

    user = it_db_session.query(User).filter_by(username="testuser").first()
    assert user is None

def test_it08_unsuccessful_registration_short_username(it_db_session, client):
    
    # Action: POST /auth/signup with a short username
    response = client.post("/auth/signup", data = {
        "username": "abc",
        "email": "test@email.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 0 # Check that there was NO redirect.
    assert b"Field must be between" in response.data

    user = it_db_session.query(User).filter_by(email="test@email.com").first()
    assert user is None

@patch('kusibot.app.auth.routes.auth_service')
def test_it09_unsuccessful_db_registration(mock_auth_service, it_db_session, client):
    
    # Mock to cause a "DB ERROR"
    mock_auth_service.register.return_value = False

    # Action: POST /auth/signup with a short username
    response = client.post("/auth/signup", data = {
        "username": "testuser",
        "email": "test@email.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    # assert len(response.history) == 0 # Check that there was NO redirect.
    assert b"An error occurred during registration." in response.data

    user = it_db_session.query(User).filter_by(email="test@email.com").first()
    assert user is None
