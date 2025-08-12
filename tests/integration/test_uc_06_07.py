import pytest
from unittest.mock import patch
from kusibot.database.models import User, Message, Assessment
from app import bcrypt

@pytest.fixture(scope="function")
def db_standard(it_db_session):
    """A database session with one registered standard user with no conversations."""

    standard_user = User(
        username = "test_user",
        email = "test@email.com",
        password = bcrypt.generate_password_hash("Password123!").decode('utf-8')
    )
    it_db_session.add(standard_user)
    it_db_session.commit()

    return it_db_session

# ---- Test for UC06 and UC07: Conduct a Chat Conversation and
# Complete an Assessment  ----

def test_it16_enter_chatbot_unauthenticated(client):
    
    # No session active
    response = client.get("/chatbot/", follow_redirects = True)

    assert response.status_code == 200
    assert len(response.history) == 1 # There was a redirect to the Login page
    assert b"Login" in response.data

def test_it17_enter_chatbot_professional(it_db_session, client):
    
    # Action: POST /auth/login as Professional
    response = client.post("/auth/login", data = {
        "identifier": "test_prof_user",
        "password": "professional123",
        "remember": "False"
    }, follow_redirects = True)

    assert response.status_code == 200
    assert b"Dashboard" in response.data

    # Try entering to the Chat interface
    response = client.get("/chatbot/", follow_redirects = True)

    assert response.status_code == 403 # Access denied
    assert b"Forbidden" in response.data

@patch('kusibot.chatbot.manager_agent.ConversationAgent')
@patch('kusibot.chatbot.manager_agent.AssesmentAgent')
def test_it18_detect_normal_intent(mock_assessment_agent, mock_conversation_agent, db_standard, client):
    
    # 1. Log in a Standard user
    standard_user_login(client)

    # 2. Setup mocks
    mock_conversation_agent_instance = mock_conversation_agent.return_value
    mock_conversation_agent_instance.generate_response.return_value = "Hello! Doing great :) How about you?"
    mock_assessment_agent_instance = mock_assessment_agent.return_value # Assessment mocked but not expected to be called.

    # 3. Action: Send a message to the chat
    response = client.post("/chatbot/chat", json={
        "message": "Hello! How are you doing KusiBot?"
    })

    # 4. Assertions
    assert response.status_code == 200
    
    json_response = response.get_json()
    assert json_response["response"] == "Hello! Doing great :) How about you?"
    assert json_response["agent_type"] == "Conversation"
    assert json_response["intent"] == "Normal"

    mock_conversation_agent_instance.generate_response.assert_called_once()
    mock_assessment_agent_instance.generate_response.assert_not_called()

    messages_stored = db_standard.query(Message)\
                             .filter_by(conversation_id="1")\
                             .all()
    assert len(messages_stored) == 3 # Checking messages are stored (1. Greeting 2. User 3. Bot)
    assert len(list(filter(lambda message: message.is_user, messages_stored))) == 1
    assert len(list(filter(lambda message: not message.is_user, messages_stored))) == 2

    # 5. Log out
    standard_user_logout(client)

@patch('kusibot.chatbot.manager_agent.ConversationAgent')
@patch('kusibot.chatbot.manager_agent.AssesmentAgent')
def test_it19_detect_distress_intent(mock_assessment_agent, mock_conversation_agent, db_standard, client):
    
    # 1. Log in a Standard user
    standard_user_login(client)

    # 2. Setup mocks
    mock_conversation_agent_instance = mock_conversation_agent.return_value
    mock_conversation_agent_instance.generate_response.return_value = "Should not be here..."
    mock_assessment_agent_instance = mock_assessment_agent.return_value
    mock_assessment_agent_instance.generate_response.return_value = "Starting an Assessment..."
    mock_assessment_agent_instance.map_intent_to_assessment.return_value = "PHQ-9"

    # 3. Action: Send a message to the chat
    response = client.post("/chatbot/chat", json={
        "message": "I think I have depression."
    })

    # 4. Assertions
    assert response.status_code == 200
    
    json_response = response.get_json()
    assert json_response["response"] == "Starting an Assessment..."
    assert json_response["agent_type"] == "Assesment"
    assert json_response["intent"] == "Depression"
    
    mock_conversation_agent_instance.generate_response.assert_not_called()
    mock_assessment_agent_instance.generate_response.assert_called_once()

    # 5. Log out
    standard_user_logout(client)

@patch('kusibot.chatbot.assesment_agent.AssesmentAgent._load_questionnaires')
def test_it20_complete_assessment(mock_questionnaires, db_standard, client):

    # 1. Mock the questionnaires to simplify it
    mock_questionnaires_data = {
        "PHQ-9": {
            "title": "Patient Health Questionnaire (PHQ-9)",
            "description": "A description...",
            "questions": [
                {
                    "id": 1,
                    "question": "Over the last 2 weeks, how often have you been bothered by little interest or pleasure in doing things",
                    "options": [
                        "Not at all",
                        "Several days",
                        "More than half the days",
                        "Nearly every day"
                    ]
                }
            ],
            "interpretations": {
                "0-4": "Minimal depression",
                "5-9": "Mild depression",
            },
            "intent": "depression"
        }
    }
    mock_questionnaires.return_value = mock_questionnaires_data

    # 2. Log-in Standard user
    standard_user_login(client)

    # 3. Trigger assessment
    client.post("/chatbot/chat", json={"message": "I think I have depression."})

    # 4. Provide free-text answer
    client.post("/chatbot/chat", json={"message": "For several dats now..."})

    # 5. Provide categorical answer
    response = client.post("/chatbot/chat", json={"message": "2"})
    json_response = response.get_json()

    # 6. Assertions
    assert response.status_code == 200
    assert "thank" in json_response["response"].lower()
    assert "Assesment" in json_response["agent_type"]

    assessment = db_standard.query(Assessment).all()
    assert len(assessment) == 1
    assessment = assessment[0]
    assert assessment is not None
    assert assessment.end_time is not None
    assert assessment.total_score == 1
    assert assessment.interpretation == "Minimal depression"

    # 7. Log out
    standard_user_logout(client)

    


@patch('kusibot.chatbot.manager_agent.AssesmentAgent')
@patch('kusibot.chatbot.manager_agent.ConversationAgent')
def test_it21_no_assessment_available(mock_conversation_agent, mock_assessment_agent, db_standard, client):
    
    # 1. Log in a Standard user
    standard_user_login(client)

    # 2. Setup mocks
    mock_conversation_agent_instance = mock_conversation_agent.return_value
    mock_conversation_agent_instance.generate_response.return_value = "I don't know how to assess with that. But Im here to listen."
    mock_assessment_agent_instance = mock_assessment_agent.return_value
    mock_assessment_agent_instance.map_intent_to_assessment.return_value = None

    # 3. Action: Send a message to the chat
    response = client.post("/chatbot/chat", json={
        "message": "I just want to die"
    })

    # 4. Assertions
    assert response.status_code == 200
    
    json_response = response.get_json()
    print(json_response)
    assert json_response["response"] == "I don't know how to assess with that. But Im here to listen."
    assert json_response["agent_type"] == "Conversation"
    assert json_response["intent"] == "Suicidal"
    
    mock_conversation_agent_instance.generate_response.assert_called_once()
    mock_assessment_agent_instance.generate_response.assert_not_called()
    mock_assessment_agent_instance.map_intent_to_assessment.assert_called_once_with("Suicidal")

    # 5. Log out
    standard_user_logout(client)

@patch('kusibot.services.chatbot_service.ChatbotManagerAgent')
def test_it22_ai_error_response(mock_manager_agent, db_standard, client):
    
    # 1. Log in a Standard user
    standard_user_login(client)

    # 2. ManagerAgent raises an exception
    mock_manager_agent_instance = mock_manager_agent.return_value
    mock_manager_agent_instance.generate_bot_response.side_effect = Exception("Ollama connection failed")

    # 3. User sends a message
    response = client.post("/chatbot/chat", json={
        "message": "This will cause an error..."
    })

    # 4. Assertions
    assert response.status_code == 500
    json_response = response.get_json()
    assert json_response["response"] == "An error occurred. Sorry for the inconvenience :("

    # 5. Logout
    standard_user_logout(client)



# ---- Utils functions ----

def standard_user_login(client):
    """Log-in a Standard user."""
    
    # Action: POST /auth/login as Professional
    response = client.post("/auth/login", data = {
        "identifier": "test_user",
        "password": "Password123!",
        "remember": "False"
    }, follow_redirects = True)

    assert response.status_code == 200

def standard_user_logout(client):
    """Log-out a Standard user."""

    response = client.get("/auth/logout", follow_redirects = True)
    assert response.status_code == 200
