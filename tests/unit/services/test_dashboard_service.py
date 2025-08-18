# Test dependencies
import pytest
from unittest.mock import patch, MagicMock
# Members used in Tests
from kusibot.services.dashboard_service import DashboardService
from kusibot.database.models import User, Conversation, Message, Assessment, AssessmentQuestion

# ---- Fixtures ----

@pytest.fixture
def mock_user_repo():
    """Provides a mock instance of the UserRepository used in DashboardService."""
    
    with patch('kusibot.services.dashboard_service.UserRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_conv_repo():
    """Provides a mock instance of the ConversationRepository used in DashboardService."""
    
    with patch('kusibot.services.dashboard_service.ConversationRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_msg_repo():
    """Provides a mock instance of the MessageRepository used in DashboardService."""
    
    with patch('kusibot.services.dashboard_service.MessageRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_assess_repo():
    """Provides a mock instance of the AssessmentRepository used in DashboardService."""
    
    with patch('kusibot.services.dashboard_service.AssessmentRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_assess_question_repo():
    """Provides a mock instance of the AssessmentQuestionRepository used in DashboardService."""
    
    with patch('kusibot.services.dashboard_service.AssessmentQuestionRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def dashboard_service():
    """Provides an instance of DashboardService for each test."""
    return DashboardService()


# ---- Tests ----

def test_ut05_get_chat_users_some_registered(mock_user_repo, dashboard_service):
    
    # Mocking the UserRepository call.
    mock_user_repo.get_non_professional_users.return_value = [
        User(username="user1", email="user1@email.com", password="pass1"),
        User(username="user2", email="user1@email.com", password="pass2"),
    ]
    
    result = dashboard_service.get_chat_users()
    assert len(result) == 2
    assert result[0]["username"] == "user1"
    assert result[1]["username"] == "user2"

def test_ut06_get_chat_users_no_registered(mock_user_repo, dashboard_service):
    
    # Mocking the UserRepository call.
    mock_user_repo.get_non_professional_users.return_value = []
    
    result = dashboard_service.get_chat_users()
    assert result == []

def test_ut07_get_conversation_for_user_some_conversations(mock_conv_repo, mock_msg_repo ,dashboard_service):
    
    # Mocking the ConversationRepository and MessagesRepository call
    mock_conv_repo.get_all_conversations_by_user_id.return_value = [Conversation(
        id = 1, user_id = 1
    )]
    mock_msg_repo.get_messages_by_conversation_id.return_value = [
        Message(conversation_id = 1, text="Hello", is_user=True),
        Message(conversation_id = 1, text="Hi there!", is_user=False)
    ]

    result = dashboard_service.get_conversations_for_user(1)
    
    assert result["conversations"] is not None
    assert result["conversations"][0]["id"] == 1
    assert result["conversations"][0]["finished_at"] is None
    
    result = dashboard_service.get_conversation_messages(1)

    assert result["messages"] is not None
    assert len(result["messages"]) == 2
    assert result["messages"][0]["text"] == "Hello"
    assert result["messages"][1]["text"] == "Hi there!"

def test_ut08_get_conversation_for_user_no_conversations(mock_conv_repo, mock_msg_repo, dashboard_service):
    
    # Mocking the ConversationRepository and MessageRepository call
    mock_conv_repo.get_all_conversations_by_user_id.return_value = None
    mock_msg_repo.get_messages_by_conversation_id.return_value = None

    result = dashboard_service.get_conversations_for_user(1)
    assert len(result["conversations"]) == 0
    result = dashboard_service.get_conversation_messages(1)
    assert len(result["messages"]) == 0

def test_ut09_get_assessments_for_user_assessment_taken(mock_assess_repo, mock_assess_question_repo, dashboard_service):
    
    # Mocking the AssessmentRepository and AssessmentQuestionRepository call
    mock_assess_repo.get_assessments_by_user_id.return_value = [Assessment(
        id = 1, user_id = 1, assessment_type = "PHQ-9", message_trigger = "I'm bad...",
        current_question = 1, current_state = "WaitingForCategorisation"
    )]
    mock_assess_question_repo.get_question_by_assessment_id.return_value = [
        AssessmentQuestion(
            id = 1, assessment_id = 1, question_number = 1, question_text = "How have you been lately?", 
            user_response = "Pretty bad as I said..."
        )
    ]

    result = dashboard_service.get_assessments_for_user(1)
    assert len(result["assessments"]) == 1
    assert result["assessments"][0]["id"] == 1
    assert result["assessments"][0]["assessment_type"] == "PHQ-9"
    assert len(result["assessments"][0]["questions"]) == 1
    assert result["assessments"][0]["questions"][0]["id"] == 1
    assert result["assessments"][0]["questions"][0]["question_text"] == "How have you been lately?"
