import pytest
from app import create_app
from kusibot.database.db import db as _db

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



