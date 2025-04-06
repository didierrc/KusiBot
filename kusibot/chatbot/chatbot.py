from kusibot.chatbot.intent_recognizer_agent import IntentRecognizerAgent
from kusibot.chatbot.conversation_agent import ConversationAgent
from kusibot.chatbot.assesment_agent import AssesmentAgent
from kusibot.database.db_repositories import ConversationRepository, MessageRepository, AssessmentRepository

class Chatbot:
    """
    Cental chatbot class that coordinates the different agents to generate a response to the user.

    The chatbot is composed of the following agents:
    - IntentRecognizerAgent: Determines the intent of the user input.
    - ConversationAgent: Generates a response to the user input for "NORMAL" intents.
    - AssesmentAgent: Generates a response to the user input for the rest of the intents and start and assesment.
    """
    
    CHATBOT_CONFIDENCE_ASSESMENT_THRESHOLD = 0.5
    CHATBOT_START_CONV_MSG = "Hello! I'm Kusibot and I'm here to chat with you about how you're feeling today."
    CHATBOT_MAX_RETRIEVE_MSG = 10
    CHATBOT_ASSESSMENT_AGENT_TYPE = "Assesment"
    CHATBOT_CONVERSATION_AGENT_TYPE = "Conversation"

    def __init__(self):
        
        # Initialize the agents
        self.intent_recognizer = IntentRecognizerAgent()
        self.conversation_agent = ConversationAgent()
        self.assesment_agent = AssesmentAgent()
        
        # Repositories used
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()
        self.assessment_repo = AssessmentRepository()

    def get_response(self, user_input, user_id):
        
        # Get the current conversation for the user
        current_conv = self.conv_repo.get_current_conversation_by_user_id(user_id)

        # Getting the current assessment if any
        assesment_active = self.assessment_repo.get_current_assessment(user_id)
        if assesment_active:
            response, agent = self.assesment_agent.generate_response(user_input, current_conv.id)
        else:
            response, agent = self._handle_response_when_no_assesment(user_input, current_conv.id)

        # Storing bot response
        self.msg_repo.save_chatbot_message(
            conv_id=current_conv.id,
            msg=response,
            intent=None,
            agent_type=agent
        )
            
        return response
            
    def create_or_get_conversation(self, user_id):
        """
        Creates a new conversation for the authenticated user or gets the current conversation.
        
        ## Parameters
        - user_id: ID of the current user to retrieve the conversation from.

        ## Returns
        - messages Represent all the messages for the new/current conversation.
        """
            
        # Get the current conversation for the user
        current_conv = self.conv_repo.get_current_conversation_by_user_id(user_id)
            
        # If there is no current conversation...
        if not current_conv:

            # Create a new one
            current_conv = self.conv_repo.create_conversation(user_id)

            # Save the initial message from the chatbot
            if current_conv:
                self.msg_repo.save_chatbot_message(
                    current_conv.id,
                    self.CHATBOT_START_CONV_MSG,
                    intent="Greeting"
                )

        # Either a new conversation was created or the current one was found, return the messages
        messages = self.msg_repo.get_limited_messages(conv_id=current_conv.id, 
                                                    limit=self.CHATBOT_MAX_RETRIEVE_MSG)
        messages.reverse()
        
        return [{'text': msg.text, 'is_user': msg.is_user} for msg in messages]
    
    def _handle_response_when_no_assesment(self, user_input, conversation_id):
        
        # If there is no current assessment, we need to get the intent of the user input.
        # To know if we need to start an assessment or just return a normal response.
        intent, confidence = self.intent_recognizer.predict_intent(user_input, return_confidence=True)
        
        # If BERT has low confidence in the intent or the intent is "Normal", we just return a normal response.
        if confidence < self.CHATBOT_CONFIDENCE_ASSESMENT_THRESHOLD or intent == "Normal":
            return self.conversation_agent.generate_response(user_input, conversation_id, intent)
        else: # Start a new assesment --> Signs of depression, anxiety, etc.
            
            if self.assesment_agent.map_intent_to_assessment(intent): # If there is a questionnaire for the intent. Start it.
                return self.assesment_agent.generate_response(user_input, conversation_id, intent)
            else:  # If there is no questionnaire for the intent, just return a response from conversational agent.
                return self.conversation_agent.generate_response(user_input, conversation_id, intent)
