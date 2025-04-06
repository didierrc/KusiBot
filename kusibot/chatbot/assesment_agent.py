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

    MODEL_PROMPT_QUESTION = """
# Agent Role & Tone:
You are an assistant within a mental health chatbot (KUSIBOT). Adopt a gentle, calm, supportive, and natural conversational style.

# Task:
Generate a **single, concise sentence (strictly 1 sentence max)** that naturally introduces the *topic* 
of the upcoming assessment question ({question}). Your primary goal is to make this introduction feel like a smooth, 
integrated part of the ongoing conversation, leveraging the `context`.
**Crucially: Do NOT state the actual assessment question itself.** Your sentence is purely a transition phrase to its general theme.

# Input Information:
* Upcoming Question Topic: {question}  # A brief description of the theme of the question to be asked next.
* Upcoming Question ID: {question_id} # The sequence number (1, 2, 3...).
* Recent Conversation Context (Last 6 messages): {context} # The recent interaction history. For question_id > 1, this includes the user's response(s) to previous question(s).

# Generation Rules:

1.  **If Question ID (`question_id`) is 1:**
    * Use the `context` to formulate a sentence that gently transitions from the general chat or the trigger for the assessment into the first question's topic (`{question}`). 
    Acknowledge the start of this focused part of the conversation.
    * *Example Goal:* Make the user feel comfortable starting the assessment based on what was just discussed.

2.  **If Question ID (`question_id`) is greater than 1:**
    * Use the latest messages in the `context` (likely the user's answer to the previous question) to create a sentence that flows naturally into the `upcoming_question` topic (`{question}`).
    * The sentence should feel like a logical continuation or the next step, based on the immediately preceding exchange visible in the `context`.
    * *Example Goal:* Ensure the sequence of questions feels connected and conversational, not abrupt, by linking to the user's last input implicitly or explicitly.

3.  **Always:**
    * Prioritize a natural, flowing conversational feel.
    * Maintain a supportive and gentle tone.
    * Strictly adhere to the 1-sentence limit.
    * Focus *only* on introducing the topic (`{question}`), not the specifics of the assessment question.

# Output Format:
Output *only* the single introduction sentence. Do not add any extra text, explanations, or greetings.

Your Response:
    """

    AGENT_TYPE = "Assesment"
    CONTEXT_MAX_RETRIEVAL = 6

    def __init__(self, model_name="mistral"):
        
        # Load Mistral Ollama model
        try:
            self.model = OllamaLLM(model=model_name)
        except Exception as e:
          print(f"ERROR: Ollama is not installed - {e}")
          self.model = None
        
        self.prompt_question = ChatPromptTemplate.from_template(self.MODEL_PROMPT_QUESTION)

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

        chain = self.prompt_question | self.model  
        
        return chain.invoke({"question": question, "question_id": question_id, "context": chat_history})
                
