from unittest.mock import patch
from kusibot.database.models import User

# ---- Test for UC08, UC09 and UC10: Professional Interactions  ----

def test_it23_enter_dashboard_unauthenticated(client):
    # No session active
    response = client.get("/dashboard/", follow_redirects = True)

    assert response.status_code == 200
    assert len(response.history) == 1 # There was a redirect to the Login page
    assert b"Login" in response.data

def test_it24_enter_dashboard_standard(db_uc_08, client):
    
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

def test_it25_enter_dashboard_professional(db_uc_08, client):
    
    # Action: POST /auth/login as Standard
    response = professional_login(client)

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    for user_number in range(1,5):
        user = "user" + str(user_number)
        assert bytes(user, "utf-8") in response.data

    professional_logout(client)

def test_it26_filter_user_list(db_uc_08, client):
    pass

@patch('kusibot.app.dashboard.routes.dashboard_service')
def test_it27_error_fetching_users(mock_service, it_db_session, client):
    
    # 1. Mocking the dashboard service to generate a DB error
    mock_service.get_chat_users.side_effect = Exception("An exception while fetching...")

    # 2. Log-in of Professional
    response = professional_login(client)

    # 3. Asserts (dashboard should display an error message)
    assert b"There was an error while fetching the users. Try again later." in response.data

def test_it28_dashboard_see_last_conversation(db_uc_08, client):
    
    # Get user under test
    user1 = db_uc_08.query(User).filter_by(username="user1").first()

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

def test_it29_dashboard_see_no_conversation(db_uc_08,client):
    
    # Get user under test
    user2 = db_uc_08.query(User).filter_by(username="user2").first()

    # 1. Action: POST /auth/login as Standard
    professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/conversations?user_id={user2.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert json["conversation"] is None
    assert json["messages"] is None

    professional_logout(client)

def test_it30_dashboard_see_assessments(db_uc_08,client):
    
    # Get user under test
    user3 = db_uc_08.query(User).filter_by(username="user3").first()

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

def test_it31_dashboard_see_no_assessments(db_uc_08,client):
    
    # Get user under test
    user1 = db_uc_08.query(User).filter_by(username="user1").first()

    # 1. Action: POST /auth/login as Standard
    response = professional_login(client)

    # 2. Action GET /dashboard/conversations
    response = client.get(f"/dashboard/assessments?user_id={user1.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert len(json["assessments"]) == 0

def test_it32_dashboard_detail_complete_assessment(db_uc_08,client):
    
    # Get user under test
    user3 = db_uc_08.query(User).filter_by(username="user3").first()

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

def test_it33_dashboard_detail_incomplete_assessment(db_uc_08, client):
    
    # Get user under test
    user4 = db_uc_08.query(User).filter_by(username="user4").first()

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