from kusibot.chatbot.dialogue_manager_agent import DialogueManagerAgent
from kusibot.chatbot.conversation_agent import ConversationAgent

# Other constants
CONFIDENCE_INTENT_THRESHOLD = 0.5

class Chatbot:
    """
    Cental chatbot class that coordinates the different agents to generate a response to the user.

    The chatbot is composed of the following agents:
    - DialogueManagerAgent: Determines the intent of the user input.
    - ConversationAgent: Generates a response to the user input for "NORMAL" intents.
    - AssesmentAgent: Generates a response to the user input for the rest of the intents and start and assesment.
    """
    
    def __init__(self):
        """Initialises the chatbot agents."""

        self.dialogue_manager = DialogueManagerAgent()
        #self.conversation_agent = ConversationAgent()

    def get_response(self, user_input, user_id):
        """Generates a response to the user input based on the selected agent."""
        
        intent, confidence =  self.dialogue_manager.predict_intent(user_input, return_confidence=True)

        if confidence < CONFIDENCE_INTENT_THRESHOLD or intent == "Normal":
            return "Hello" #self.conversation_agent.generate_response(user_input, intent, user_id)
        else:
            return f"Bot: I think you are talking about {intent} with a confidence of {confidence:.2f}"