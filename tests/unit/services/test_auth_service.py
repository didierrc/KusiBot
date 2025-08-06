# Test dependencies
import pytest
from unittest.mock import patch, MagicMock
# Members used in Tests
from kusibot.services.auth_service import AuthService
from kusibot.database.models import User

# ---- Fixtures ----

@pytest.fixture
def mock_user_repo():
    """Provides a mock instance of the UserRepository used in AuthService."""

    with patch('kusibot.services.auth_service.UserRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def auth_service():
    """Provides an instance of AuthService for each test."""
    return AuthService()

# ---- Tests ----

def test_ut01a_possible_login_nonexisting_identifier(mock_user_repo, auth_service):

    # Mocking the repository calls.
    mock_user_repo.get_user_by_email.return_value = None
    mock_user_repo.get_user_by_username.return_value = None

    # Email not found...
    result = auth_service.possible_login("unknown@example.com", "password")
    assert result is None

    # Username not found...
    result = auth_service.possible_login("unknown", "password")
    assert result is None

def test_ut01a_possible_login_wrong_password(mock_user_repo, auth_service):

    # Mocking the repository calls.
    mock_user = User(username="test_user", email="test@email.com", password="password")
    mock_user.check_password = MagicMock(return_value=False)
    mock_user_repo.get_user_by_email.return_value = mock_user
    mock_user_repo.get_user_by_username.return_value = mock_user

    # Username found but incorrect password...
    result = auth_service.possible_login("test_user", "wrong_password")
    assert result is None

    # Email found but incorrect password...
    result = auth_service.possible_login("test@email.com", "wrong_password")
    assert result is None

def test_ut02_valid_credentials(mock_user_repo, auth_service):

    # Mocking the repository calls.
    mock_user = User(username="test_user", email="test@email.com", password="password")
    mock_user.check_password = MagicMock(return_value=True)
    mock_user_repo.get_user_by_email.return_value = mock_user
    mock_user_repo.get_user_by_username.return_value = mock_user

    # Valid Username and Password...
    result = auth_service.possible_login("test_user", "password")
    assert result == mock_user

    # Valid Email and Password...
    result = auth_service.possible_login("test@email.com", "password")
    assert result == mock_user

@patch('app.bcrypt')
def test_ut03_register_valid_credentials(mock_bcrypt, mock_user_repo, auth_service):

    # Mocking bcrypt and repository calls
    mock_bcrypt.generate_password_hash.return_value.decode.return_value = "hashed_password"
    mock_user_repo.add_user.return_value = User(username="newuser", email="new@example.com", password="hashed_password")

    # Successful registration
    result = auth_service.register("newuser", "new@example.com", "password123")
    assert result is True

@patch('app.bcrypt')
def test_ut04_register_valid_credentials(mock_bcrypt, mock_user_repo, auth_service):

    # Mocking bcrypt and repository calls
    mock_bcrypt.generate_password_hash.return_value.decode.return_value = "hashed_password"
    mock_user_repo.add_user.return_value = None # Failure in repo as unique constraint has been violated

    # Successful registration
    result = auth_service.register("newuser", "new@example.com", "password123")
    assert result is False

