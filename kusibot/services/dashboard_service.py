from kusibot.database.db_repositories import(
    UserRepository,
    ConversationRepository,
    MessageRepository,
    AssessmentRepository,
    AssessmentQuestionRepository
)

class DashboardService:
    """Service class for handling dashboards interactions.

    Attributes:
        user_repo (UserRepository): Repository for user data access.
        conv_repo (ConversationRepository): Repository for conversation data access.
        msg_repo (MessageRepository): Repository for message data access.
        assessment_repo (AssessmentRepository): Repository for assessment data access.
        assesment_question_repo (AssessmentQuestionRepository): Repository for
            assessment question data access.
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()
        self.assessment_repo = AssessmentRepository()
        self.assesment_question_repo = AssessmentQuestionRepository()

    def get_chat_users(self):
        """
        Retrieves a list of non-professional users for the dashboard.
        
        Returns:
            list: A list of dictionaries containing user IDs and usernames.
        """
        
        users = self.user_repo.get_non_professional_users()

        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username
            })

        return user_data 
    
    def get_conversations_for_user(self, user_id):
        """
        Retrieves the conversation history for a given user.
        
        Args:
            user_id: The ID of the user for whom to retrieve the conversation.
        Returns:
            dict: A dictionary containing the conversation history with the needed details.
        """

        response = {
            'conversations': []
        }

        # Getting all the conversations
        conversations = self.conv_repo.get_all_conversations_by_user_id(user_id)
        if not conversations:
            return response
        
        for conversation in conversations:
            response['conversations'].append({
                'id': conversation.id,
                'created_at': conversation.created_at,
                'finished_at': conversation.finished_at
            })

        return response
    
    def get_conversation_messages(self, conversation_id):
        """
        Retrieves the messages of a specific conversation by its ID.
        
        Args:
            conversation_id: The ID of the conversation to retrieve.
        Returns:
            dict: A dictionary containing the conversation messages.
        """

        response = {
            'messages': []
        }

        # Getting the messages for the conversation
        messages = self.msg_repo.get_messages_by_conversation_id(conversation_id)
        if not messages:
            return response
        
        for message in messages:
            response['messages'].append({
                'id': message.id,
                'text': message.text,
                'timestamp': message.timestamp,
                'is_user': message.is_user,
                'intent': message.intent
            })

        return response
        
    def get_assessments_for_user(self, user_id):
        """
        Retrieves assessments and their questions for a given user.
        
        Args:
            user_id: The ID of the user for whom to retrieve assessments.
        Returns:
            dict: A dictionary containing the assessments and their questions.
        """

        response = {
            'assessments': []
        }

        assessments = self.assessment_repo.get_assessments_by_user_id(user_id)
        if not assessments:
            return response
        else:
            for assessment in assessments:

                assesment_questions = self.assesment_question_repo.get_question_by_assessment_id(assessment.id)
                questions = []
                if assesment_questions:
                    for question in assesment_questions:
                        questions.append({
                            'id': question.id,
                            'question_number': question.question_number,
                            'question_text': question.question_text,
                            'user_response': question.user_response,
                            'categorized_value': question.categorized_value,
                            'timestamp': question.timestamp
                        })

                response['assessments'].append({
                    'id': assessment.id,
                    'assessment_type': assessment.assessment_type,
                    'message_trigger': assessment.message_trigger,
                    'start_time': assessment.start_time,
                    'end_time': assessment.end_time,
                    'total_score': assessment.total_score,
                    'interpretation': assessment.interpretation,
                    'questions': questions
                })

        
        return response
        
