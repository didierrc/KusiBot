import pytest
from app import bcrypt
from kusibot.database.models import User, Conversation, Assessment

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

# ---- Test for UC05: Log Out of the System ----

def test_it15_successful_logout(db_uc05, client):
    
    # 1. Needed a logged-in standard user
    response = client.post("/auth/login", data = {
        "identifier": "test_user",
        "password": "Password123!",
        "remember": "False"
    }, follow_redirects = True)

    # Assert user is logged-in and in the chatbot (Test it10)
    assert response.status_code == 200
    assert b"KusiChat" in response.data

    # 2. Log out
    response = client.get("/auth/logout", follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert len(response.history) == 1 # Check that there was one redirect to the main page.
    assert b"Welcome to KusiBot" in response.data

    # Check active conversation and assessment is finished
    active_conversation = db_uc05.query(Conversation).filter_by(id=1).first()
    active_assessment = db_uc05.query(Assessment).filter_by(id=1).first()
    assert active_conversation.finished_at is not None
    assert active_assessment.end_time is not None



