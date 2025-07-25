from kusibot.database.db_repositories import ConversationRepository, MessageRepository, AssessmentRepository
from kusibot.chatbot import ChatbotManagerAgent

class ChatbotService:
    """Service class for handling chatbot interactions."""
    
    CHATBOT_MAX_RETRIEVE_MSG = 10
    CHATBOT_START_CONV_MSG = "Hello! I'm Kusibot and I'm here to chat with you about how you're feeling today."
    CHATBOT_NO_MSG_PROVIDED = 'Sorry, but you didn\'t provide any message.'
    CHATBOT_NO_CONVERSATION = 'No current conversation found. Please start a new conversation.'

    def __init__(self):
        """
        Initialises the ChatbotService class with their needed repositories.
        """
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()
        self.assessment_repo = AssessmentRepository()
        self.user_agents = {}

    def create_or_get_conversation(self, user_id):
        """
        Creates a new conversation for the authenticated user or gets the current conversation.
        
        Parameters
            user_id: ID of the current user to retrieve or create the conversation from.
        Returns
            messages: Array of JSON messages for the new/current conversation.
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

        # Create a new user agent for the user if it doesn't exist
        self._get_or_create_chatbot_manager(user_id)

        # Either a new conversation was created or the current one was found, return the messages
        messages = self.msg_repo.get_limited_messages(conv_id=current_conv.id, 
                                                      limit=self.CHATBOT_MAX_RETRIEVE_MSG)
        messages.reverse()
        
        return [{'text': msg.text, 
                 'is_user': msg.is_user,
                 'timestamp': msg.timestamp.isoformat() + 'Z'} 
                 for msg in messages]
    
    def get_response(self, user_input, user_id):
        """
        Generates a response from the chatbot.
        
        Parameters
            user_input: The message sent by the user.
            user_id: ID of the user making the request.
        Returns
            response: The chatbot's response to the user's input.
        """

        # Get the current conversation for the user
        current_conv = self.conv_repo.get_current_conversation_by_user_id(user_id)
        
        # If there is no current conversation, create a new one
        if not current_conv:
            return self.CHATBOT_NO_CONVERSATION
        
        # Get the correct chatbot manager for the user.
        user_agent = self._get_or_create_chatbot_manager(user_id)

        # Response generation based on whether an assessment is active or not
        bot_response = user_agent.generate_bot_response(user_input, user_id, current_conv.id)

        # Saving user message first
        self.msg_repo.save_user_message(conv_id=current_conv.id,
                                        msg=user_input,
                                        intent=bot_response["intent_detected"])

        # Storing bot response after
        self.msg_repo.save_chatbot_message(conv_id=current_conv.id,
                                           msg=bot_response["agent_response"],
                                           intent=None,
                                           agent_type=bot_response["agent_type"]
        )
            
        return bot_response["agent_response"]

    def _get_or_create_chatbot_manager(self, user_id):
        """
        Gets or creates a ChatbotManagerAgent for the user to handle chatbot interactions
        keeping user-specific state and conversation management.
        
        Parameters
            user_id: ID of the user to get or create the chatbot manager for.
        Returns
            ChatbotManagerAgent: The chatbot manager for the user.
        """
        
        if user_id not in self.user_agents:
            self.user_agents[user_id] = ChatbotManagerAgent()
        return self.user_agents[user_id]

    def _clear_user_agent(self, user_id):
        """
        Clears the chatbot manager for the user, effectively resetting their state.
        
        Parameters
            user_id: ID of the user to clear the chatbot manager for.
        """
        
        if user_id in self.user_agents:
            del self.user_agents[user_id]

    def end_conversation(self, user_id):
        """
        Ends the current conversation and clear the user agent for the authenticated user.
        
        Parameters
            user_id: ID of the current user to end the conversation for.
        Returns
            bool: True if the conversation was successfully ended, False otherwise.
        """

        # Clear the user agent to reset the state
        self._clear_user_agent(user_id)

        # Get the current conversation for the user
        current_conv = self.conv_repo.get_current_conversation_by_user_id(user_id)

        # If there is a current conversation, end it
        if current_conv:
            self.conv_repo.end_conversation(current_conv.id)
            return True
            
        return False
    
chatbot_service = ChatbotService() # Singleton instance of ChatbotService