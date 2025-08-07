# Test dependencies
import pytest
from unittest.mock import patch, MagicMock
# Members used in Tests
from kusibot.chatbot.manager_agent import ChatbotManagerAgent
from kusibot.chatbot.assesment_agent import AssesmentAgent

# ---- Fixtures ----

@pytest.fixture
def manager_agent():
    """Provides an instance of ManagerAgent for each test."""
    return ChatbotManagerAgent()

@pytest.fixture
def mock_intent_agent_in_manager_agent():
    """Provides a mock instance of the IntentRecogniserAgent used in ManagerAgent."""

    with patch('kusibot.chatbot.manager_agent.IntentRecognizerAgent') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_conversation_agent_in_manager_agent():
    """Provides a mock instance of the ConversationAgent used in ManagerAgent."""

    with patch('kusibot.chatbot.manager_agent.ConversationAgent') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_assessment_agent_in_manager_agent():
    """Provides a mock instance of the AssesmentAgent used in ManagerAgent."""

    with patch('kusibot.chatbot.manager_agent.AssesmentAgent') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_assessment_repo_in_manager_agent():
    """Provides a mock instance of the AssesmentRepository used in ManagerAgent."""

    with patch('kusibot.chatbot.manager_agent.AssessmentRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        yield mock_repo
 
# ---- Tests ----

def test_ut13_generate_bot_response_assessment_agent(mock_assessment_repo_in_manager_agent,
                                                     mock_intent_agent_in_manager_agent,
                                                     mock_assessment_agent_in_manager_agent,
                                                     mock_conversation_agent_in_manager_agent,
                                                     manager_agent):
    # Setting up the Mocks
    mock_assessment_repo_in_manager_agent.is_assessment_active.return_value = False
    mock_intent_agent_in_manager_agent.predict_intent.return_value = ("Depression", 0.9)
    mock_assessment_agent_in_manager_agent.map_intent_to_assessment.return_value = "PHQ-9"

    # Test
    manager_agent.generate_bot_response("I'm feeling down", 1, 1)
    mock_assessment_agent_in_manager_agent.generate_response.assert_called_once()
    mock_conversation_agent_in_manager_agent.generate_response.assert_not_called()

def test_ut14_generate_bot_response_assessment_agent(mock_assessment_repo_in_manager_agent,
                                                     mock_intent_agent_in_manager_agent,
                                                     mock_assessment_agent_in_manager_agent,
                                                     mock_conversation_agent_in_manager_agent,
                                                     manager_agent):
    
    # Setting up the Mocks
    mock_assessment_repo_in_manager_agent.is_assessment_active.return_value = False
    mock_intent_agent_in_manager_agent.predict_intent.return_value = ("Normal", 0.8)
    mock_assessment_agent_in_manager_agent.map_intent_to_assessment.return_value = None

    # Test
    manager_agent.generate_bot_response("Hello there!", 1, 1)
    mock_assessment_agent_in_manager_agent.generate_response.assert_not_called()
    mock_conversation_agent_in_manager_agent.generate_response.assert_called_once()

def test_ut15_map_intent_to_assessment():
    
    agent = AssesmentAgent()

    # Testing Anxiety intents return GAD-7 assessment
    result = agent.map_intent_to_assessment("anxiety")
    assert result == "GAD-7"

    # Testing Depression intents return PHQ-9 assessment
    result = agent.map_intent_to_assessment("depression")
    assert result == "PHQ-9"

