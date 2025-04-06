from kusibot.database.db import db
from kusibot.database.models import Conversation, Message, Assessment, AssessmentQuestion, User
from sqlalchemy import func
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt

class UserRepository:

    def get_user_by_username(self, username):
        try:
            return db.session.query(User).filter_by(username=username).first()
        except Exception as e:
            print(f"Error retrieving user by username: {e}")
            db.session.rollback()
            return None
        
    def add_user(self, username, email, password, is_professional=False):
        try:
            # Hash the password
            hashed_password = Bcrypt().generate_password_hash(password).decode('utf-8')
            # Create a new professional user
            professional = User(username=username,
                                email=email,
                                password=hashed_password,
                                created_at=datetime.now(timezone.utc),
                                is_professional=is_professional)
            db.session.add(professional)
            db.session.commit()
            return professional
        except Exception as e:
            print(f"Error adding user: {e}")
            db.session.rollback()
            return None

class ConversationRepository:

    def get_current_conversation_by_user_id(self, user_id):
        try:
            return db.session.query(Conversation)\
                             .filter_by(user_id=user_id, finished_at=None)\
                             .first()
        except Exception as e:
            print(f"Error retrieving current conversation: {e}")
            db.session.rollback()
            return None
        
    def create_conversation(self, user_id):
        try:
            new_conversation = Conversation(user_id=user_id,
                                            created_at=datetime.now(timezone.utc))
            db.session.add(new_conversation)
            db.session.commit()
            return new_conversation
        except Exception as e:
            print(f"Error creating conversation: {e}")
            db.session.rollback()
            return None
        
    def get_conversation(self, conv_id):
        try:
            return db.session.query(Conversation).filter_by(id=conv_id).first()
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            db.session.rollback()
            return None
        
    def end_conversation(self, conv_id):
        try:
            conversation = self.get_conversation(conv_id)
            if conversation:
                conversation.finished_at = datetime.now(timezone.utc)
                db.session.commit()
        except Exception as e:
            print(f"Error ending conversation: {e}")
            db.session.rollback()

class MessageRepository:

    def save_chatbot_message(self, conv_id, msg, intent=None, agent_type="Conversation"):
        try:
            message = Message(
                conversation_id=conv_id,
                text=msg,
                timestamp=datetime.now(timezone.utc),
                is_user=False,
                intent=intent,
                agent_type=agent_type
            )
            db.session.add(message)
            db.session.commit()
        except Exception as e:
            print(f"Error saving chatbot message: {e}")
            db.session.rollback()

    def save_user_message(self, conv_id, msg, intent=None):
        try:
            message = Message(
                conversation_id=conv_id,
                text=msg,
                timestamp=datetime.now(timezone.utc),
                is_user=True,
                intent=intent,
            )
            db.session.add(message)
            db.session.commit()
        except Exception as e:
            print(f"Error saving user message: {e}")
            db.session.rollback()

    def get_limited_messages(self, conv_id, limit):
        try:
            return db.session.query(Message)\
                             .filter_by(conversation_id=conv_id)\
                             .order_by(Message.timestamp.desc())\
                             .limit(limit)\
                             .all()
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            db.session.rollback()
            return []
    
class AssessmentRepository:

    def get_current_assessment(self, user_id):
        try:
            return db.session.query(Assessment)\
                             .filter_by(user_id=user_id, end_time=None)\
                             .first()
        except Exception as e:
            print(f"Error retrieving current assessment: {e}")
            db.session.rollback()
            return None
        
    def get_assessment(self, assessment_id):
        try:
            return db.session.query(Assessment).filter_by(id=assessment_id).first()
        except Exception as e:
            print(f"Error retrieving assessment: {e}")
            db.session.rollback()
            return None
        
    def create_assessment(self, user_id, assessment_type, state):
        try:
            new_assessment = Assessment(
                user_id=user_id,
                assessment_type=assessment_type,
                start_time=datetime.now(timezone.utc),
                current_state=state
            )
            db.session.add(new_assessment)
            db.session.commit()
            return new_assessment
        except Exception as e:
            print(f"Error creating assessment: {e}")
            db.session.rollback()
            return None
        
    def update_assessment(self, assessment_id, **kwargs):
        try:
            assessment = self.get_assessment(assessment_id)
            if assessment:
                for key, value in kwargs.items():
                    setattr(assessment, key, value)
                db.session.commit()
        except Exception as e:
            print(f"Error updating assessment: {e}")
            db.session.rollback()

    def calculate_total_score(self, assessment_id):
        try:
            total_score = db.session.query(func.sum(AssessmentQuestion.categorized_value))\
                                    .filter(AssessmentQuestion.assessment_id == assessment_id)\
                                    .scalar()
            return total_score if total_score is not None else 0
        except Exception as e:
            print(f"Error calculating total score: {e}")
            db.session.rollback()
            return 0

class AssessmentQuestionRepository:
    
    def get_question_by_assessment_id(self, assessment_id):
        try:
            return db.session.query(AssessmentQuestion)\
                             .filter_by(assessment_id=assessment_id)\
                             .order_by(AssessmentQuestion.question_number)\
                             .all()
        except Exception as e:
            print(f"Error retrieving questions: {e}")
            db.session.rollback()
            return []
    
    def save_assessment_question(self, assessment_id, question_number, question_text, user_response, categorized_value):
        try:
            assessment_question = AssessmentQuestion(
                assessment_id=assessment_id,
                question_number=question_number,
                question_text=question_text,
                user_response=user_response,
                categorized_value=categorized_value,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(assessment_question)
            db.session.commit()
        except Exception as e:
            print(f"Error saving assessment question: {e}")
            db.session.rollback()