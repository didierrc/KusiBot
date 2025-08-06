# Members used in Tests
from kusibot.database.db_repositories import UserRepository, ConversationRepository, AssessmentRepository
from kusibot.database.models import User, Conversation, Assessment, AssessmentQuestion

def test_ut10a_get_user_by_username_not_found(unit_test_db_session):
    
    repo = UserRepository()
    result = repo.get_user_by_username("unknown")
    assert result is None

def test_ut10b_get_user_by_username_found(unit_test_db_session):
    
    # Add a new user to the test DB
    unit_test_db_session.add(
        User(username="user1", 
             email="user1@email.com", 
             password="pass1")
    )
    unit_test_db_session.commit()

    # Test
    repo = UserRepository()
    result = repo.get_user_by_username("user1")
    assert result is not None
    assert result.username == "user1"

def test_ut11_end_conversation(unit_test_db_session):
    
    # Adds an active Conversation
    test_user = User(id = 1, username="user1", email="user1@email.com", password="pass1")
    test_conv = Conversation(id = 1, user_id = test_user.id)
    unit_test_db_session.add_all([test_user, test_conv])
    unit_test_db_session.commit()

    # Test
    repo = ConversationRepository()
    repo.end_conversation(test_conv.id)

    unit_test_db_session.refresh(test_conv)
    assert test_conv.finished_at is not None

def test_ut12_calculate_total_score_for_assessment(unit_test_db_session):
    
    # Adds a taken assessment with answered questions to a new user.
    test_user = User(id = 1, username = 'user1', email = 'user1@email.com', password = 'pass1')
    test_assessment = Assessment(id = 1, user_id = test_user.id, assessment_type = "PHQ-9", 
                                 message_trigger = "I've been feeling lonely...", current_question = 3,
                                 current_state = "Finished")
    q1 = AssessmentQuestion(id = 1, assessment_id = test_assessment.id, question_number = 1, 
                            question_text = "Q1?", user_response = "UR1", categorized_value = 3)
    q2 = AssessmentQuestion(id = 2, assessment_id = test_assessment.id, question_number = 2, 
                            question_text = "Q2?", user_response = "UR2", categorized_value = 2)
    q3 = AssessmentQuestion(id = 3, assessment_id = test_assessment.id, question_number = 3, 
                            question_text = "Q3?", user_response = "UR3", categorized_value = 1)
    unit_test_db_session.add_all([test_user, test_assessment, q1, q2, q3])
    unit_test_db_session.commit()

    # Test
    repo = AssessmentRepository()
    total_score = repo.calculate_total_score(test_assessment.id)
    assert total_score == 6 # 3 + 2 + 1