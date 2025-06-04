from kusibot.chatbot.intent_recognizer_agent import IntentRecognizerAgent
from kusibot.chatbot.conversation_agent import ConversationAgent
from kusibot.chatbot.assesment_agent import AssesmentAgent
from kusibot.database.db_repositories import AssessmentRepository

class ChatbotManagerAgent:
    """
    Cental chatbot class that coordinates the different agents to generate a response to the user.

    The chatbot is composed of the following agents:
    - IntentRecognizerAgent: Determines the intent of the user input.
    - ConversationAgent: Generates a response to the user input for "NORMAL" intents.
    - AssesmentAgent: Generates a response to the user input for the rest of the intents and start and assesment.
    """
    
    CHATBOT_CONFIDENCE_ASSESMENT_THRESHOLD = 0.5    
    CHATBOT_ASSESSMENT_AGENT_TYPE = "Assesment"
    CHATBOT_CONVERSATION_AGENT_TYPE = "Conversation"

    def __init__(self):
        """
        Initialises the chatbot manager agent with all the agents on its control.
        - IntentRecognizerAgent: For intent recognition.
        - ConversationAgent: For generating responses to normal intents.
        - AssesmentAgent: For generating responses when an assesment is ongoing or to administer one.
        """
        
        self.intent_recognizer = IntentRecognizerAgent()
        self.conversation_agent = ConversationAgent()
        self.assesment_agent = AssesmentAgent()

        self.assessment_repo = AssessmentRepository()

    def generate_bot_response(self, user_input, user_id, conv_id):
        """
        Orchestrates agents to generate a bot response based on the user input and the current conversation.
        
        Parameters
            user_input: The message sent by the user.
            conv_id: ID of the current conversation.
            assesment_active: Boolean indicating if an assessment is currently active for the user.
        Returns
            response: JSON chatbot response.
        """
        
        assesment_active = self.assessment_repo.is_assessment_active(user_id)

        response = {
            "intent_detected": None,
            "agent_response": None,
            "agent_type": self.CHATBOT_ASSESSMENT_AGENT_TYPE
        } # By default, response is when assessment is active.

        if assesment_active:
            
            response["agent_response"] =  self.assesment_agent.generate_response(user_input, conv_id)
        
        else:
            
            agent_response = self._handle_response_when_no_assesment(user_input, conv_id)
            response["intent_detected"] = agent_response["intent_detected"]
            response["agent_response"] = agent_response["response"]
            response["agent_type"] = agent_response["type"]
            
        return {
            "intent_detected": response["intent_detected"],
            "agent_response": response["agent_response"],
            "agent_type": response["agent_type"]
        }
            
    def _handle_response_when_no_assesment(self, user_input, conversation_id):
        """
        Handles the response generation when there is no active assessment.
        Determines the intent of the user input and decides whether to start an assessment or return a normal response.

        Parameters
            user_input: The message sent by the user.
            conversation_id: ID of the current conversation.
        Returns
            agent_response: JSON response containing the intent detected, response generated, and agent type.
        """
        
        agent_response = {
            "intent_detected": None,
            "response": None,
            "type": None
        }

        # If there is no current assessment, we need to get the intent of the user input.
        # To know if we need to start an assessment or just return a normal response.
        intent, confidence = self.intent_recognizer.predict_intent(user_input)
        agent_response["intent_detected"] = intent

        # If BERT has low confidence in the intent or the intent is "Normal", we just return a normal response.
        response = None
        if confidence < self.CHATBOT_CONFIDENCE_ASSESMENT_THRESHOLD or intent == "Normal":
            
            response = self.conversation_agent.generate_response(user_input, conversation_id, intent)
            agent_response["type"] = self.CHATBOT_CONVERSATION_AGENT_TYPE

        else: # Start a new assesment --> Signs of depression, anxiety, etc.
            
            if self.assesment_agent.map_intent_to_assessment(intent): # If there is a questionnaire for the intent. Start it.
                
                response = self.assesment_agent.generate_response(user_input, conversation_id, intent)
                agent_response["type"] = self.CHATBOT_ASSESSMENT_AGENT_TYPE
            
            else:  # If there is no questionnaire for the intent, just return a response from conversational agent.
                
                response = self.conversation_agent.generate_response(user_input, conversation_id, intent)
                agent_response["type"] = self.CHATBOT_CONVERSATION_AGENT_TYPE
        
        agent_response["response"] = response
        return agent_response

