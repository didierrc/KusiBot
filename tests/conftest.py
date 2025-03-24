import pytest
from flask_login import login_user
from kusibot.database.db import db
from kusibot.database.models import User
from app import create_app, bcrypt


@pytest.fixture(scope='function')
def app():
    """Create and configure a Flask app for testing."""
    
    app = create_app('testing') # Creates a Flask app with memory db.

    with app.app_context():
        
        # Create fresh database tables.
        db.create_all()

        # Add a test user.
        test_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
        test_user = User(username='test_user',email='test@example.com',password=test_pwd)
        db.session.add(test_user)
        db.session.commit()

        yield app

        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def authenticated_client(app, client):
    """An already authenticated user."""
    with app.test_request_context():
        user = User.query.filter_by(email='test@example.com').first()
        login_user(user)
        
        # Get a new test client with the session setup
        with client.session_transaction() as session:
            session['_user_id'] = user.id
            
    return client