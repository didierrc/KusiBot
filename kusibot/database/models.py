from kusibot.database.db import db
from datetime import datetime, timezone
from flask_login import UserMixin

#############################################################
# SQLAlchemy models for the database                        #
# https://flask-sqlalchemy.readthedocs.io/en/stable/models/ #
#############################################################

class User(UserMixin, db.Model):
    """
    User model for the database.

    Attributes:
        id (int): User ID.
        username (str): User's username.
        email (str): User's email.
        password (str): User's password.
        created_at (datetime): User's account creation date.
        is_professional (bool): True if the user is a professional (can go into dashboard), False if it's a simple user.
        conversations (Relationship): Relationship with the Conversation model.
        assessments (Relationship): Relationship with the Assessment model.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    is_professional = db.Column(db.Boolean, default=False)
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    assessments = db.relationship('Assessment', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username!r}. Email: {self.email!r}. Professional: {self.is_professional!r}>'
    
    def check_password(self, password):
        """
        Check if the provided password matches the user's password.

        Parameters:
            password (str): The password to check.
        
        Returns:
            bool: True if the password matches, False otherwise.
        """
        
        from app import bcrypt
        return bcrypt.check_password_hash(self.password, password)

class Conversation(db.Model):
    """
    Conversation model for the database.

    Attributes:
        id (int): Conversation ID.
        user_id (int): User ID that started the conversation.
        created_at (datetime): Conversation creation date.
        finished_at (datetime): Conversation finish date.
        messages (Relationship): Relationship with the Message model.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)
    messages = db.relationship('Message', backref='conversation', lazy=True)

    def __repr__(self):
        return f'<Conversation {self.id!r}. User: {self.user_id!r}. Created at: {self.created_at!r}>'

class Message(db.Model):
    """
    Message model for the database.

    Attributes:
        id (int): Message ID.
        conversation_id (int): Conversation ID that the message belongs to.
        text (str): Message text.
        timestamp (datetime): Message timestamp.
        is_user (bool): True if the message is from the user, False if it's from chatbot.
        intent (str): Intent of the message if detected.
        agent_type (str): Type of agent that answered the message (Conversarion or Assesment agent).
    """

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    is_user = db.Column(db.Boolean, nullable=False)
    intent = db.Column(db.String(50), nullable=True)
    agent_type = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Message {self.id!r}. Conversation: {self.conversation_id!r}. Timestamp: {self.timestamp!r}. Is user: {self.is_user!r}. Intent: {self.intent!r}. Agent type: {self.agent_type!r}>'

class Assessment(db.Model):
    """
    Assessment model for the database.

    Attributes:
        id (int): Assessment ID.
        user_id (int): User ID that took the assessment.
        assessment_type (str): Type of assessment (e.g., 'PHQ-9').
        start_time (datetime): Start time of the assessment.
        end_time (datetime): End time of the assessment.
        total_score (int): Total score of the assessment.
        interpretation (str): Interpretation of the assessment.
        questions (Relationship): Relationship with the AssessmentQuestion model.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)
    total_score = db.Column(db.Integer, nullable=True)
    interpretation = db.Column(db.String(100), nullable=True)

    # Assesment State
    current_question = db.Column(db.Integer, default=1, nullable=False)
    current_state = db.Column(db.String(30), nullable=False) 
    last_free_text = db.Column(db.Text, nullable=True)

    questions = db.relationship('AssessmentQuestion', backref='assessment', lazy=True)

    def __repr__(self):
        return f'<Assessment {self.id!r}. User: {self.user_id!r}. Type: {self.assessment_type!r}. Total score: {self.total_score!r}. Interpretation: {self.interpretation!r}>'

class AssessmentQuestion(db.Model):
    """
    AssessmentQuestion model for the database.

    Attributes:
        id (int): AssessmentQuestion ID.
        assessment_id (int): Assessment ID that the question belongs to.
        question_number (int): Question number.
        question_text (str): Question text.
        user_response (str): User response to the question.
        categorized_value (int): Mapped to standard scale.
        timestamp (datetime): Question timestamp
    """

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    user_response = db.Column(db.Text, nullable=False)  # Free text response
    categorized_value = db.Column(db.Integer, nullable=True)  # Mapped to standard scale
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<AssessmentQuestion {self.id!r}. Assessment: {self.assessment_id!r}. Question number: {self.question_number!r}. User response: {self.user_response!r}. Categorized value: {self.categorized_value!r}>'