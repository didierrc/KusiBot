import pytest, sys, time, statistics
from app import create_app, bcrypt
from kusibot.database.db import db as _db
from kusibot.database.models import User

@pytest.fixture(scope="session")
def performance_app():
    yield create_app(config_name="performance")

@pytest.fixture(scope="function")
def performance_db_session(performance_app):
    
    with performance_app.app_context():
        _db.create_all()
         
        standard_user = User(
            username = "test_user",
            email = "test_user@email.com",
            password = bcrypt.generate_password_hash("password").decode('utf-8'),
            is_professional = False
        )

        _db.session.add(standard_user)
        _db.session.commit()
        yield _db.session
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope="function")
def performance_client(performance_app):
    """
    Creates a test client for the Flask application.
    It allows making HTTP requests to the app's endpoint.
    """
    return performance_app.test_client()

def normal_test(performance_client, iteration):
    
    print(f"Iteration {iteration}")

    # 1. Log in as Standard user
    response = performance_client.post("/auth/login", data = {
        "identifier": "test_user",
        "password": "password",
        "remember": "False"
    }, follow_redirects = True)

    # 2. Scenario: Normal messages
    normal_messages = [
        "Hello, how are you?",
        "Hey kusibot, can you hellp me with something?",
        "Im feeling pretty exited today!",
        "I HAVE A SECRET TO TELL :)",
        "how u doing champ?"
    ]
    normal_timings = []

    # 3. Sending messages
    for message in normal_messages:
        
        start_time = time.perf_counter()
        response = performance_client.post("/chatbot/chat", json={"message": message})
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        normal_timings.append(elapsed_time)

        assert response.status_code == 200
        msg_to_print = f"  - Message: '{message}' | Response Time: {elapsed_time:.4f} seconds "
        msg_to_print += f"| Response: {response.json.get('response', 'No response')[1:10]} ({response.json.get('intent', 'No intent')})"
        print(msg_to_print)

    # 4. Log out as Standard user
    response = performance_client.get("/auth/logout", follow_redirects = True)
    assert response.status_code == 200

    return normal_timings

def test_response_time_normal(performance_db_session, performance_client):
    
    print("\n--- Running KusiBot Performance Tests (I) ---\n")

    print("Measuring 'Normal Conversation' response times...\n")
    normal_iterations = 1
    for iteration in range(normal_iterations):
        timings = normal_test(performance_client, iteration + 1)
        avg_time = statistics.mean(timings)
        print(f"\nAverage Response Time for Iteration {iteration + 1}: {avg_time:.4f} seconds")

def assessment_test(performance_client, iteration):

    print(f"Iteration {iteration}")

    # 1. Scenario: Assessment messages
    assessment_messages = ["I think I have depression", "I've been feeling anxious lately"]
    assessment_timings = []

    # 2. Sending messages
    for message in assessment_messages:

        # 3. Log in as Standard user
        response = performance_client.post("/auth/login", data = {
            "identifier": "test_user",
            "password": "password",
            "remember": "False"
        }, follow_redirects = True)
        
        start_time = time.perf_counter()
        response = performance_client.post("/chatbot/chat", json={"message": message})
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        assessment_timings.append(elapsed_time)

        assert response.status_code == 200
        msg_to_print = f"  - Message: '{message}' | Response Time: {elapsed_time:.4f} seconds "
        msg_to_print += f"| Response: {response.json.get('response', 'No response')[1:10]} ({response.json.get('intent', 'No intent')})"
        print(msg_to_print)

        # 4. Need to Log out to reset the conversation
        response = performance_client.get("/auth/logout", follow_redirects = True)
        assert response.status_code == 200

        return assessment_timings

def test_response_time_assessment(performance_db_session, performance_client):
    
    print("\n--- Running KusiBot Performance Tests (II) ---\n")

    print("\nMeasuring 'Assessment Initiation' response times...")
    assessment_iterations = 1
    for iteration in range(assessment_iterations):
        timings = assessment_test(performance_client, iteration + 1)
        avg_time = statistics.mean(timings)
        print(f"\nAverage Response Time for Iteration {iteration + 1}: {avg_time:.4f} seconds")


    
