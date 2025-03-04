from flask_sqlalchemy import SQLAlchemy
import datetime

#########################################
# SQLAlchemy models for the database
#########################################

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    is_professional = db.Column(db.Boolean, default=False) # True if the user is a professional (can go into dashboard), False if it's a simple user.
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    assessments = db.relationship('Assessment', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username!r}. Email: {self.email!r}. Professional: {self.is_professional!r}>'

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)
    messages = db.relationship('Message', backref='conversation', lazy=True)

    def __repr__(self):
        return f'<Conversation {self.id!r}. User: {self.user_id!r}. Created at: {self.created_at!r}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    is_user = db.Column(db.Boolean, nullable=False) # True if the message is from the user, False if it's from chatbot.
    intent = db.Column(db.String(50), nullable=True) # Intent of the message if detected.
    agent_type = db.Column(db.String(20), nullable=True) # Type of agent that answered the message (Conversarion or Assesment agent).

    def __repr__(self):
        return f'<Message {self.id!r}. Conversation: {self.conversation_id!r}. Timestamp: {self.timestamp!r}. Is user: {self.is_user!r}. Intent: {self.intent!r}. Agent type: {self.agent_type!r}>'

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type = db.Column(db.String(20), nullable=False)  # e.g., 'PHQ-9'
    start_time = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)
    total_score = db.Column(db.Integer, nullable=True)
    interpretation = db.Column(db.String(100), nullable=True)
    questions = db.relationship('AssessmentQuestion', backref='assessment', lazy=True)

    def __repr__(self):
        return f'<Assessment {self.id!r}. User: {self.user_id!r}. Type: {self.assessment_type!r}. Total score: {self.total_score!r}. Interpretation: {self.interpretation!r}>'

class AssessmentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    user_response = db.Column(db.Text, nullable=False)  # Free text response
    categorized_value = db.Column(db.Integer, nullable=True)  # Mapped to standard scale
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AssessmentQuestion {self.id!r}. Assessment: {self.assessment_id!r}. Question number: {self.question_number!r}. User response: {self.user_response!r}. Categorized value: {self.categorized_value!r}>'