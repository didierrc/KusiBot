import json, os
from langchain_ollama import OllamaLLM
from kusibot.chatbot.assesment_states.asking_question_state import AskingQuestionState
from kusibot.database.db_repositories import AssessmentRepository, ConversationRepository, MessageRepository, AssessmentQuestionRepository
from langchain_core.prompts import ChatPromptTemplate

class AssesmentAgent:
    """
    Handles assesment conversation flow when distress intent is detected by BERT.
    """

    STATE_ASKING = "asking_question"
    STATE_WAITING_FREE_TEXT = "waiting_free_text"
    STATE_WAITING_CATEGORIZATION = "waiting_categorization"
    STATE_FINISHED = "finished"

    MODEL_PROMPT = """
    You are a friendly assistant in a mental health chatbot. 
    Generate a short, natural lead-in phrase (1 sentence max) to gently introduce an assessment question."
    Do NOT ask the actual question. The question is about: '{question}'. "
    Generate ONLY the lead-in phrase taking in mind the following rules:
    - If the ID of the question is 1: Generate the lead-in phrase based on the conversation context.
    - If the ID is other than 1: Generate the lead-in phrase based on the previous question.
    Question ID: {question_id}
    Context: {context}
    Your Response:"
    """

    AGENT_TYPE = "Assesment"
    CONTEXT_MAX_RETRIEVAL = 4

    def __init__(self, model_name="mistral"):
        
        # Load Mistral Ollama model
        try:
            self.model = OllamaLLM(model=model_name)
        except Exception as e:
          print(f"ERROR: Ollama is not installed - {e}")
          self.model = None
        
        self.prompt = ChatPromptTemplate.from_template(self.MODEL_PROMPT)

        # Load questionnaire data
        self.questionnaires = self._load_questionnaires()

        # Initial assessment state is asking question.
        self.transition_to_next_state(AskingQuestionState())

        # Repositories
        self.conv_repo = ConversationRepository()
        self.assess_repo = AssessmentRepository()
        self.msg_repo = MessageRepository()
        self.assess_question_repo = AssessmentQuestionRepository()
        
    def _load_questionnaires(self):
        
        # Construct path relative to the current file for robustness
        base_dir = os.path.dirname(os.path.abspath(__file__)) 
        file_path = os.path.join(base_dir, 'questionnaires', 'questionnaires.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Questionnaire file not found at {file_path}")
            return {} 
        except json.JSONDecodeError:
            print(f"ERROR: Failed to decode JSON from {file_path}")
            return {}
        
    def transition_to_next_state(self, state):
        self.state = state
        self.state.context = self

        print(f"AssesmentAgent: Transitioning from {type(self.state).__name__} --> {type(state).__name__}")

    def map_intent_to_assessment(self, intent):
        for questionnaire_key, questionnaire_data in self.questionnaires.items():
            if questionnaire_data['intent'] == intent.lower():
                return questionnaire_key
        return None
    
    def get_question_json(self, assessment_id):
        try:
            # Get the current assessment
            assesment = self.assess_repo.get_assessment(assessment_id)

            # Get the question to ask
            question_list = self.questionnaires[assesment.assessment_type]['questions']
            for question in question_list:
                if question['id'] == assesment.current_question:
                    return question
            return None
        except (KeyError, IndexError, TypeError) as e:
            print(f"ERROR: Failed to get question JSON: {e}")
            return None

    def generate_response(self, user_input, conversation_id, intent=None):
        
        # Storing user message
        self.msg_repo.save_user_message(
          conv_id=conversation_id,
          msg=user_input,
          intent=intent
        )

        # Get the current conversation and assesment
        current_conv = self.conv_repo.get_conversation(conversation_id)
        current_assesment = self.assess_repo.get_current_assessment(current_conv.user_id)

        # If there is no current assessment, we need to start a new one.
        if not current_assesment:
            # Validation of questionnaire existence is done in ConversationAgent!! 
            # Shouldn't reach here if questionnaire does not exist.
            questionnaire_to_take = self.map_intent_to_assessment(intent)
        
            current_assesment = self.assess_repo.create_assessment(user_id=current_conv.user_id,
                                               assessment_type=questionnaire_to_take,
                                               state=self.STATE_ASKING
                                            )
        
        # Process response based on STATE
        return self.state.generate_response(user_input, 
                                            conversation_id, 
                                            current_assesment.id), self.AGENT_TYPE

    def naturalize_question(self, question, question_id, user_id):
        
        # If model not available, return the question as is
        if not self.model:
            return question
        
        # Get the context for the question
        current_conv = self.conv_repo.get_current_conversation_by_user_id(user_id)
        messages = self.msg_repo.get_limited_messages(current_conv.id, self.CONTEXT_MAX_RETRIEVAL)
        messages.reverse()
        
        chat_history = "\n".join([f"{'User' if msg.is_user else 'Bot'}: {msg.text}" for msg in messages])

        chain = self.prompt | self.model  
        
        return chain.invoke({"question": question, "question_id": question_id, "context": chat_history})
                
