from kusibot.database.db import db
from kusibot.database.models import Conversation, Message, Assessment, AssessmentQuestion
from sqlalchemy import func

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
            new_conversation = Conversation(user_id=user_id)
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
        
class MessageRepository:

    def save_chatbot_message(self, conv_id, msg, intent=None, agent_type="Conversation"):
        try:
            message = Message(
                conversation_id=conv_id,
                text=msg,
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
    
    def save_assessment_question(self, assessment_id, question_number, question_text, user_response, categorized_value):
        try:
            assessment_question = AssessmentQuestion(
                assessment_id=assessment_id,
                question_number=question_number,
                question_text=question_text,
                user_response=user_response,
                categorized_value=categorized_value
            )
            db.session.add(assessment_question)
            db.session.commit()
        except Exception as e:
            print(f"Error saving assessment question: {e}")
            db.session.rollback()