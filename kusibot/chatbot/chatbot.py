from kusibot.chatbot.dialogue_manager_agent import DialogueManagerAgent
from kusibot.chatbot.conversation_agent import ConversationAgent
from flask import current_app
from kusibot.database.models import Conversation, Message
from kusibot.database.db import db

CONFIDENCE_INTENT_THRESHOLD = 0.5
CHATBOT_GREETING = "Hello! I'm Kusibot and I'm here to chat with you about how you're feeling today."
CONVERSATION_MAX_RETRIEVAL = 10

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
        self.conversation_agent = ConversationAgent()
        self.current_intent = ""

    def get_response(self, user_input, user_id):
        """
        Generates a response to the user input based on its intent.
        
        ## Parameters
        - user_input: The user input text.
        - user_id: ID of the current user.

        ## Returns
        - str: The chatbot response. 
        """
        
        with current_app.app_context():
            # Get conversation
            current_conv = Conversation.query.filter_by(user_id=user_id, finished_at=None).first()
            if not current_conv: # Should not happen but just in case
                current_conv = Conversation(user_id=user_id)
                db.session.add(current_conv)
                db.session.commit()
            
            # Getting Intent from BERT
            intent, confidence =  self.dialogue_manager.predict_intent(user_input, return_confidence=True)
            self.current_intent = intent

            # Storing user input with intent
            self._save_message(conv_id=current_conv.id, 
                               text=user_input,
                               is_user=True,
                               intent=intent)

            # ROUTING LOGIC
            if confidence < CONFIDENCE_INTENT_THRESHOLD or intent == "Normal":
                response = self.conversation_agent.generate_response(user_input, current_conv.id)
                agent = "Conversation"
            else: # HERE THE ASSESMENT AGENT
                response = f"I think you are talking about {intent} with a confidence of {confidence:.2f}"
                agent = "Assesment"

            # Storing the bot response
            self._save_message(conv_id=current_conv.id,
                               text=response,
                               is_user=False,
                               intent=None,
                               agent_type=agent)
            
    def create_or_get_conversation(self, user_id):
        """
        Creates a new conversation for the authenticated user or gets the current conversation.
        
        ## Parameters
        - user_id: ID of the current user to retrieve the conversation from.

        ## Returns
        - messages Represent all the messages for the new/current conversation.
        """
        with current_app.app_context():
            
            current_conv = Conversation.query.filter_by(user_id=user_id, finished_at=None).first()
            
            if not current_conv:
                # If there is no active conversation, create a new one with a greeting.
                current_conv = Conversation(user_id=user_id)
                db.session.add(current_conv)
                db.session.commit()
                self._save_message(
                    current_conv.id,
                    CHATBOT_GREETING,
                    is_user=False,
                    intent="Greeting",
                    agent_type="Conversation"
                )
            
            messages = Message.query.filter_by(conversation_id=current_conv.id)\
                                    .order_by(Message.timestamp.asc())\
                                    .limit(CONVERSATION_MAX_RETRIEVAL)\
                                    .all()
            return [{'text': msg.text, 'is_user': msg.is_user} for msg in messages]
        
    def _save_message(self, conv_id, text, is_user, intent=None, agent_type=None):
        """Saves a message into the database for the given conversation (private method)"""
        message = Message(
            conversation_id=conv_id, 
            text=text, 
            is_user=is_user, 
            intent=intent,
            agent_type=agent_type
        )
        db.session.add(message)
        db.session.commit()