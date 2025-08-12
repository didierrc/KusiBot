import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, bcrypt
from datetime import datetime, timezone, timedelta
from kusibot.database.db import db as _db
from kusibot.database.models import User, Conversation, Assessment, Message, AssessmentQuestion

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

@pytest.fixture(scope="function")
def db_uc05(it_db_session):
    """A database session with one registered standard user and
    an active conversation and assessment."""

    standard_user = User(
        username = "test_user",
        email = "test@email.com",
        password = bcrypt.generate_password_hash("Password123!").decode('utf-8')
    )
    it_db_session.add(standard_user)
    it_db_session.commit()
    it_db_session.refresh(standard_user)

    active_conversation = Conversation(user_id = standard_user.id)
    it_db_session.add(active_conversation)

    active_assessment = Assessment( 
        user_id = standard_user.id,
        assessment_type = "PHQ-9",
        message_trigger = "I've been feeling bad...",
        current_question = 1,
        current_state = "Finished"
    )
    it_db_session.add(active_assessment)
    
    it_db_session.commit()

    return it_db_session

@pytest.fixture(scope="function")
def db_uc_06(it_db_session):
    """A database session with one registered standard user with no conversations."""

    standard_user = User(
        username = "test_user",
        email = "test@email.com",
        password = bcrypt.generate_password_hash("Password123!").decode('utf-8')
    )
    it_db_session.add(standard_user)
    it_db_session.commit()

    return it_db_session

@pytest.fixture(scope="function")
def db_uc_08(it_db_session):
    """A database session with registered standard users with useful data."""

    # Create four users...
    for user_number in range(1,5):
        username = "user" + str(user_number)
        email = username + "@email.com"
        it_db_session.add(User(username=username, email=email, 
                               password=bcrypt.generate_password_hash("Password123!").decode("utf-8")))
    it_db_session.commit()

    # USER 1 - two conversations with messages -> use in it24, it26, it28, it31
    user1 = it_db_session.query(User).filter_by(username="user1").first()
    
    old_conv = Conversation(user=user1, 
                            created_at=datetime.now(timezone.utc) - timedelta(days=2), 
                            finished_at=datetime.now(timezone.utc) - timedelta(days=1))
    new_conv = Conversation(user=user1)
    old_msg = Message(conversation=old_conv, text="Hello in the past...", is_user=True)
    new_msg = Message(conversation=new_conv, text="Hello now...", is_user=True)
    it_db_session.add_all([old_conv, old_msg, new_conv, new_msg])

    # USER 2 - no conversations -> use in it26, it29
    # USER 3 - single conversation that triggered an assessment and all questions answered -> use to it30, it32
    # (Assessment of a single question)
    user3 = it_db_session.query(User).filter_by(username="user3").first()

    conv3 = Conversation(user=user3)
    msg_array3 = [Message(conversation=conv3, text="I think I may have depression...", is_user=True, intent="Depression"),
                 Message(conversation=conv3, text="Hey, let me help you with that...", is_user=False, agent_type="Assesment"),
                 Message(conversation=conv3, text="Yeah I have been feeling that way since...", is_user=True),
                 Message(conversation=conv3, text="I feel you...Scale it...", is_user=False, agent_type="Assesment"),
                 Message(conversation=conv3, text="2", is_user=True),
                 Message(conversation=conv3, text="That's all. Thanks for sharing...", is_user=False, agent_type="Assesment")]
    assess3 = Assessment(user=user3, assessment_type="PHQ-9", message_trigger="I think I may have depression...",
                         start_time=datetime.now(timezone.utc) - timedelta(minutes=10),
                         end_time=datetime.now(timezone.utc) - timedelta(minutes=5),
                         total_score=2,
                         interpretation="Mild depression",
                         current_question=1, current_state="Finished",
                         last_free_text="Yeah I have been feeling that way since...")
    assess_question3 = AssessmentQuestion(assessment=assess3, question_number=1,
                                          question_text="Hey, let me help you with that...",
                                          user_response="Yeah I have been feeling that way since...",
                                          categorized_value=2)
    it_db_session.add_all([conv3, *msg_array3, assess3, assess_question3])
    
    # USER 4 - single conversation that triggered an assessment (incomplete) -> it33
    user4 = it_db_session.query(User).filter_by(username="user4").first()

    conv4 = Conversation(user=user4, created_at=datetime.now(timezone.utc) - timedelta(days=2), 
                            finished_at=datetime.now(timezone.utc) - timedelta(days=1))
    msg_array4 = [Message(conversation=conv4, text="I think I may have depression...", is_user=True, intent="Depression"),
                 Message(conversation=conv4, text="Hey, let me help you with that...", is_user=False, agent_type="Assesment"),
                 Message(conversation=conv4, text="Yeah I have been feeling that way since...", is_user=True)]
    assess4 = Assessment(user=user4, assessment_type="PHQ-9", message_trigger="I think I may have depression...",
                         start_time=datetime.now(timezone.utc) - timedelta(minutes=2),
                         end_time=datetime.now(timezone.utc) - timedelta(minutes=1),
                         current_question=1, current_state="WaitingCategorisation",
                         last_free_text="Yeah I have been feeling that way since...")
    assess_question4 = AssessmentQuestion(assessment=assess4, question_number=1,
                                          question_text="Hey, let me help you with that...",
                                          user_response="Yeah I have been feeling that way since...")
    it_db_session.add_all([conv4, *msg_array4, assess4, assess_question4])
    
    
    # Commiting all changes
    it_db_session.commit()

    return it_db_session