from kusibot.database.db_repositories import(
    UserRepository,
    ConversationRepository,
    MessageRepository,
    AssessmentRepository,
    AssessmentQuestionRepository
)

class Dashboard:

    def __init__(self):
        self.user_repo = UserRepository()
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()
        self.assessment_repo = AssessmentRepository()
        self.assesment_question_repo = AssessmentQuestionRepository()

    def get_chat_users(self):
        
        users = self.user_repo.get_non_professional_users()

        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username
            })
        return user_data 
    
    def get_conversation_for_user(self, user_id):

        response = {
            'conversation': None,
            'messages': None
        }

        conversation = self.conv_repo.get_last_conversation_by_user_id(user_id)
        if not conversation:
            return response
        else:
            response['conversation'] = {
                'id': conversation.id,
                'created_at': conversation.created_at,
                'finished_at': conversation.finished_at
            }

        messages = self.msg_repo.get_messages_by_conversation_id(conversation.id)
        if not messages:
            return response
        else:
            response['messages'] = []
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
                    'start_time': assessment.start_time,
                    'end_time': assessment.end_time,
                    'total_score': assessment.total_score,
                    'interpretation': assessment.interpretation,
                    'questions': questions
                })

        
        return response
        