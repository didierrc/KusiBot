import pytest
from app import create_app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test that the home route returns a 200 status code."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data

def test_main_function():
    """Test that the main function exists."""
    from app import main
    assert callable(main)