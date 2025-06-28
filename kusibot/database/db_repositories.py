from kusibot.database.db import db
from kusibot.database.models import Conversation, Message, Assessment, AssessmentQuestion, User
from sqlalchemy import func
from datetime import datetime, timezone

class UserRepository:

    def get_user_by_username(self, username):
        """
        Retrieve a user by their username.

        Parameters:
            username (str): The username of the user to retrieve.
        Returns:
            User: The user object if found, otherwise None.
        """

        try:
            return db.session.query(User).filter_by(username=username).first()
        except Exception as e:
            print(f"Error retrieving user by username: {e}")
            db.session.rollback()
            return None
        
    def get_user_by_email(self, email):
        """
        Retrieve a user by their email.

        Parameters:
            email (str): The email of the user to retrieve.
        Returns:
            User: The user object if found, otherwise None.
        """

        try:
            return db.session.query(User).filter_by(email=email).first()
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            db.session.rollback()
            return None
        
    def add_user(self, username, email, hashed_password, is_professional):
        """
        Add a new user to the database.

        Parameters:
            username (str): The username of the new user.
            email (str): The email of the new user.
            hashed_password (str): The hashed password of the new user.
            is_professional (bool): Whether the user is a professional user or not.
        Returns:
            User: The newly created user object if successful, otherwise None.
        """

        try:
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
        
    def get_non_professional_users(self):
        """
        Retrieve all non-professional users from the database.
        
        Returns:
            list: A list of non-professional User objects.
        """

        try:
            return db.session.query(User).filter_by(is_professional=False).all()
        except Exception as e:
            print(f"Error retrieving non-professional users: {e}")
            db.session.rollback()
            return []

class ConversationRepository:

    def get_current_conversation_by_user_id(self, user_id):
        """
        Retrieve the current conversation (not finished) for a given user.

        Parameters:
            user_id: The ID of the user whose current conversation is to be retrieved.
        Returns:
            Conversation: The current conversation object if found, otherwise None.
        """

        try:
            return db.session.query(Conversation)\
                             .filter_by(user_id=user_id, finished_at=None)\
                             .first()
        except Exception as e:
            print(f"Error retrieving current conversation: {e}")
            db.session.rollback()
            return None
        
    def get_last_conversation_by_user_id(self, user_id):
        """
        Retrieve the last conversation (finished or not) for a given user.
        
        Parameters:
            user_id: The ID of the user whose last conversation is to be retrieved.
        Returns:
            Conversation: The last conversation object if found, otherwise None.
        """

        try:
            return db.session.query(Conversation)\
                             .filter_by(user_id=user_id)\
                             .order_by(Conversation.created_at.desc())\
                             .first()
        except Exception as e:
            print(f"Error retrieving last conversation: {e}")
            db.session.rollback()
            return None
        
    def create_conversation(self, user_id):
        """
        Create a new conversation for a given user.

        Parameters:
            user_id: The ID of the user for whom the conversation is to be created.
        Returns:
            Conversation: The newly created conversation object if successful, otherwise None.
        """

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
        """
        Retrieve a conversation by its ID.
        
        Parameters:
            conv_id: The ID of the conversation to retrieve.
        Returns:
            Conversation: The conversation object if found, otherwise None.
        """

        try:
            return db.session.query(Conversation).filter_by(id=conv_id).first()
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            db.session.rollback()
            return None
        
    def end_conversation(self, conv_id):
        """
        End the given conversation by setting its finished_at timestamp.

        Parameters:
            conv_id: The ID of the conversation to end.
        """

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
        """
        Save a chatbot message to the conversation stored in database.

        Parameters:
            conv_id: The ID of the conversation to which the message belongs.
            msg: The text of the chatbot message.
            intent: The intent of the message, if applicable (generally, it does not).
            agent_type: The type of agent sending the message (default is the ConversationAgent).
        """

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
        """
        Save a user message to the conversation stored in database.
        
        Parameters:
            conv_id: The ID of the conversation to which the message belongs.
            msg: The text of the user message.
            intent: The intent of the message, if applicable.
        """

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
        """
        Retrieve the last <limit> messages from a conversation, ordered by timestamp.

        Parameters:
            conv_id: The ID of the conversation from which to retrieve messages.
            limit: The maximum number of messages to retrieve.
        Returns:
            list: A list of Message objects.
        """

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
        
    def get_messages_by_conversation_id(self, conv_id):
        """
        Retrieve all messages from a conversation, ordered by timestamp.

        Parameters:
            conv_id: The ID of the conversation from which to retrieve messages.
        Returns:
            list: A list of Message objects.
        """

        try:
            return db.session.query(Message)\
                             .filter_by(conversation_id=conv_id)\
                             .order_by(Message.timestamp)\
                             .all()
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            db.session.rollback()
            return []
    
class AssessmentRepository:

    def get_current_assessment(self, user_id):
        """
        Retrieve the current assessment (not finished) for a given user.

        Parameters:
            user_id: The ID of the user whose current assessment is to be retrieved.
        Returns:
            Assessment: The current assessment object if found, otherwise None.
        """

        try:
            return db.session.query(Assessment)\
                             .filter_by(user_id=user_id, end_time=None)\
                             .first()
        except Exception as e:
            print(f"Error retrieving current assessment: {e}")
            db.session.rollback()
            return None
        
    def is_assessment_active(self, user_id):
        """
        Check if there is an active assessment for the given user.

        Parameters:
            user_id: The ID of the user to check.
        Returns:
            bool: True if an active assessment exists, False otherwise.
        """
        return self.get_current_assessment(user_id) is not None
        
    def get_assessment(self, assessment_id):
        """
        Retrieve an assessment by its ID.

        Parameters:
            assessment_id: The ID of the assessment to retrieve.
        Returns:
            Assessment: The assessment object if found, otherwise None.
        """

        try:
            return db.session.query(Assessment).filter_by(id=assessment_id).first()
        except Exception as e:
            print(f"Error retrieving assessment: {e}")
            db.session.rollback()
            return None
        
    def create_assessment(self, message_trigger, user_id, assessment_type, state):
        """
        Create a new assessment for a given user.

        Parameters:
            user_id: The ID of the user for whom the assessment is to be created.
            assessment_type: The type of the assessment (e.g., "PHQ9", "GAD7").
            state: The initial state of the assessment (e.g., "AskingQuestion state").
        Returns:
            Assessment: The newly created assessment object if successful, otherwise None.
        """

        try:
            new_assessment = Assessment(
                user_id=user_id,
                assessment_type=assessment_type,
                message_trigger=message_trigger,
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
        """
        Update an existing assessment with new values.

        Parameters:
            assessment_id: The ID of the assessment to update.
            **kwargs: The fields to update and their new values.
        """

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
        """
        Calculate the total score of an assessment by summing the values of its questions.

        Parameters:
            assessment_id: The ID of the assessment for which to calculate the total score.
        Returns:
            int: The total score of the assessment, or 0 if no questions are found or an error occurred.
        """

        try:
            total_score = db.session.query(func.sum(AssessmentQuestion.categorized_value))\
                                    .filter(AssessmentQuestion.assessment_id == assessment_id)\
                                    .scalar()
            return total_score if total_score is not None else 0
        except Exception as e:
            print(f"Error calculating total score: {e}")
            db.session.rollback()
            return 0
        
    def get_assessments_by_user_id(self, user_id):
        """
        Retrieve all assessments for a given user, ordered by start time in descending order.

        Parameters:
            user_id: The ID of the user whose assessments are to be retrieved.
        Returns:
            list: A list of Assessment objects.
        """

        try:
            return db.session.query(Assessment)\
                             .filter_by(user_id=user_id)\
                             .order_by(Assessment.start_time.desc())\
                             .all()
        except Exception as e:
            print(f"Error retrieving assessments: {e}")
            db.session.rollback()
            return []
        
    def end_assessment(self, user_id):
        """
        End the current assessment for a given user by setting its end_time.

        Parameters:
            user_id: The ID of the user whose assessment is to be ended.
        """

        try:
            assessment = self.get_current_assessment(user_id)
            if assessment:
                assessment.end_time = datetime.now(timezone.utc)
                db.session.commit()
        except Exception as e:
            print(f"Error ending assessment: {e}")
            db.session.rollback()

class AssessmentQuestionRepository:
    
    def get_question_by_assessment_id(self, assessment_id):
        """
        Retrieve all questions for a given assessment, ordered by question number.

        Parameters:
            assessment_id: The ID of the assessment whose questions are to be retrieved.
        Returns:
            list: A list of AssessmentQuestion objects.
        """

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
        """
        Save an assessment question to the database.

        Parameters:
            assessment_id: The ID of the assessment to which the question belongs.
            question_number: The number of the question in the assessment.
            question_text: The text of the question.
            user_response: The user's free-text response to the question.
            categorized_value: The categorized value of the user's response (depends on questionnaire).
        """

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