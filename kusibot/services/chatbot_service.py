

class ChatbotService:
    

    def end_conversation(self):
        current_app.chatbot.end_conversation(current_user.id)

