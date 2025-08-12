import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from kusibot.database.models import User, Conversation, Message, Assessment, AssessmentQuestion
from app import bcrypt

@pytest.fixture(scope="function")
def db_users(it_db_session):
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

# ---- Test for UC08, UC09 and UC10: Professional Interactions  ----

def test_it23_enter_dashboard_unauthenticated(client):
    # No session active
    response = client.get("/dashboard/", follow_redirects = True)

    assert response.status_code == 200
    assert len(response.history) == 1 # There was a redirect to the Login page
    assert b"Login" in response.data

def test_it24_enter_dashboard_standard(db_users, client):
    
    # Action: POST /auth/login as Standard
    response = client.post("/auth/login", data = {
        "identifier": "user1",
        "password": "Password123!",
        "remember": "False"
    }, follow_redirects = True)

    assert response.status_code == 200
    assert b"KusiChat" in response.data

    # Try entering to the Dashboard interface
    response = client.get("/dashboard/", follow_redirects = True)

    assert response.status_code == 403 # Access denied
    assert b"Forbidden" in response.data

def test_it25_enter_dashboard_professional(db_users, client):
    
    # Action: POST /auth/login as Standard
    response = professional_login(client)

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    for user_number in range(1,5):
        user = "user" + str(user_number)
        assert bytes(user, "utf-8") in response.data

    professional_logout(client)

@patch('kusibot.app.dashboard.routes.dashboard_service')
def test_it27_error_fetching_users(mock_service, it_db_session, client):
    
    # 1. Mocking the dashboard service to generate a DB error
    mock_service.get_chat_users.side_effect = Exception("An exception while fetching...")

    # 2. Log-in of Professional
    response = professional_login(client)

    # 3. Asserts (dashboard should display an error message)
    assert b"There was an error while fetching the users. Try again later." in response.data

def test_it28_dashboard_see_last_conversation(db_users, client):
    
    # Get user under test
    user1 = db_users.query(User).filter_by(username="user1").first()

    # 1. Action: POST /auth/login as Standard
    professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/conversations?user_id={user1.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert json["conversation"] is not None
    assert len(json["messages"]) == 1
    assert json["messages"][0]["text"] == "Hello now..."

    professional_logout(client)

def test_it29_dashboard_see_no_conversation(db_users,client):
    
    # Get user under test
    user2 = db_users.query(User).filter_by(username="user2").first()

    # 1. Action: POST /auth/login as Standard
    professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/conversations?user_id={user2.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert json["conversation"] is None
    assert json["messages"] is None

    professional_logout(client)

def test_it30_dashboard_see_assessments(db_users,client):
    
    # Get user under test
    user3 = db_users.query(User).filter_by(username="user3").first()

    # 1. Action: POST /auth/login as Standard
    professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/assessments?user_id={user3.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert len(json["assessments"]) == 1
    assert json["assessments"][0]["assessment_type"] == "PHQ-9"
    assert json["assessments"][0]["message_trigger"] == "I think I may have depression..."
    assert json["assessments"][0]["interpretation"] == "Mild depression"

    professional_logout(client)

def test_it31_dashboard_see_no_assessments(db_users,client):
    
    # Get user under test
    user1 = db_users.query(User).filter_by(username="user1").first()

    # 1. Action: POST /auth/login as Standard
    response = professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/assessments?user_id={user1.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert len(json["assessments"]) == 0

def test_it32_dashboard_detail_complete_assessment(db_users,client):
    
    # Get user under test
    user3 = db_users.query(User).filter_by(username="user3").first()

    # 1. Action: POST /auth/login as Standard
    professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/assessments?user_id={user3.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert len(json["assessments"]) == 1
    assert len(json["assessments"][0]["questions"]) == 1
    assert json["assessments"][0]["total_score"] == 2
    assert json["assessments"][0]["questions"][0]["question_text"] == "Hey, let me help you with that..."
    assert json["assessments"][0]["questions"][0]["categorized_value"] == 2

def test_it33_dashboard_detail_incomplete_assessment(db_users, client):
    
    # Get user under test
    user4 = db_users.query(User).filter_by(username="user4").first()

    # 1. Action: POST /auth/login as Standard
    professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/assessments?user_id={user4.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert len(json["assessments"]) == 1
    assert len(json["assessments"][0]["questions"]) == 1
    assert json["assessments"][0]["total_score"] is None
    assert json["assessments"][0]["questions"][0]["question_text"] == "Hey, let me help you with that..."
    assert json["assessments"][0]["questions"][0]["categorized_value"] is None

# ---- Utils ----
def professional_login(client):
    
    # Action: POST /auth/login as Standard
    response = client.post("/auth/login", data = {
        "identifier": "test_prof_user",
        "password": "professional123",
        "remember": "False"
    }, follow_redirects = True)

    assert response.status_code == 200

    return response

def professional_logout(client):
    response = client.get("/auth/logout", follow_redirects = True)
    assert response.status_code == 200