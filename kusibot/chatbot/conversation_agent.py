from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from kusibot.database.db import db
from kusibot.database.models import Message

PROMPT_TEMPLATE = """
# Agent description
You are a compassionate and supportive conversational agent designed to provide empathetic 
and helpful responses in a mental health support context. You are part of a larger MAS system
where a BERT model has detected an intent and pass the response handling to you.
Your primary goals are to:
1. Maintain a supportive and non-judgmental tone
2. Listen actively and show understanding
3. Provide gentle guidance when appropriate
4. Respect user's emotional state and boundaries

# Conversation Context:
- Previous Conversation History: {chat_history}
- User Query: {user_query}

# Response Guidelines:
- Respond with empathy and understanding
- Avoid giving direct medical advice
- Encourage professional help when needed
- Maintain a calm and supportive tone
- If the conversation suggests serious mental health concerns, 
  gently suggest speaking with a mental health professional.
- Detect a possible intent of the User Query from the following list: Normal, Depression or Anxiety.
- Response format: [RESPONSE] - [DETECTED_INTENT]

Your Response:
"""

class ConversationAgent:
  """Handles normal conversation flow."""

  def __init__(self, model_name="mistral"):
    """
    Initialize the Normal Conversation Agent for mental health support.
    """
    
    try:
      self.model = OllamaLLM(model=model_name)
    except Exception as e:
      print(f"ERROR: Ollama is not installed - {e}")
      self.model = None
    
    self.prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
  def generate_response(self, text, conversation_id):
    
    if not self.model:
      return "Sorry, the model is not available at the moment and I'm not able to help you :("

    # Fetch last X messages for the context.
    from kusibot.chatbot import CONVERSATION_MAX_RETRIEVAL
    messages = Message.query.filter_by(conversation_id=conversation_id)\
                          .order_by(Message.timestamp.asc())\
                          .limit(CONVERSATION_MAX_RETRIEVAL)\
                          .all()
    chat_history = "\n".join([f"{'User' if msg.is_user else 'Bot'}: {msg.text}" for msg in messages])
    
    chain = self.prompt | self.model
  
    return chain.invoke({"chat_history": chat_history, "user_query": text})

    