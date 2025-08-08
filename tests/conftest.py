import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, bcrypt
from kusibot.database.db import db as _db
from kusibot.database.models import User

@pytest.fixture(scope="session")
def app():
    """
    Creates a Flask application instance for the test session.
    So the SQLite database is configured as an in-memory database.
    """
    
    yield create_app(config_name="testing")

@pytest.fixture(scope="function")
def unit_test_db_session(app):
    """
    Creates a database session for a single test function (only UNIT TESTING).
    - Establishes an application context.
    - Creates all database tables.
    - Yields the session for the test to use.
    - Cleans up by dropping all tables after the test.
    """

    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope="function")
def it_db_session(app):
    """
    Creates a database session for a single test function (only INTEGRATION TESTING).
    - Establishes an application context.
    - Creates all database tables.
    - Adds the Professional user
    - Yields the session for the test to use.
    - Cleans up by dropping all tables after the test.
    """

    with app.app_context():
        _db.create_all()
        
        professional_username = "test_prof_user"
        professional_password = "professional123"
        professional_email = "test_prof@email.com"
         
        pro_user = User(
            username = professional_username,
            email = professional_email,
            password = bcrypt.generate_password_hash(professional_password).decode('utf-8'),
            is_professional = True
        )

        _db.session.add(pro_user)
        _db.session.commit()
        yield _db.session
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope="function")
def client(app : Flask) -> FlaskClient:
    """
    Creates a test client for the Flask application.
    It allows making HTTP requests to the app's endpoint.
    """
    return app.test_client()
