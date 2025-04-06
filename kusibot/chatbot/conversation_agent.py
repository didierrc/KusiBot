from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from kusibot.database.db_repositories import MessageRepository

class ConversationAgent:
  """Handles normal conversation flow."""

  CONTEXT_MAX_RETRIEVE_MSG = 10
  AGENT_TYPE = "Conversation"
  MODEL_NOT_AVAILABLE_RESPONSE = "Sorry, the model is not available at the moment and I'm not able to help you :("
  PROMPT_TEMPLATE = """
# Agent description
You are KUSIBOT a supportive mental health chatbot designed to provide concise (2-3 sentences max) and
empathetic responses based on the chat history and user query. You are part of a larger MAS 
system where a BERT model has detected an intent and pass the response handling to you.
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
- Encourage professional help when needed (not always)
- Maintain a calm and supportive tone
- If the conversation suggests serious mental health concerns, 
  gently suggest speaking with a mental health professional.

Your Response:
"""

  def __init__(self, model_name="mistral"):
    """
    Initialize the Normal Conversation Agent for mental health support.
    """
    
    try:
      self.model = OllamaLLM(model=model_name)
    except Exception as e:
      print(f"ERROR: Ollama is not installed - {e}")
      self.model = None
    
    self.prompt = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)

    # Repositories used
    self.msg_repo = MessageRepository()
    
  def generate_response(self, text, conversation_id, intent=None):
    
    # Save user message
    self.msg_repo.save_user_message(
      conv_id=conversation_id,
      msg=text,
      intent=intent
    )

    if not self.model:
      return self.MODEL_NOT_AVAILABLE_RESPONSE, self.AGENT_TYPE

    # Fetch last X messages for the context.
    messages = self.msg_repo.get_limited_messages(
      conv_id=conversation_id,
      limit=self.CONTEXT_MAX_RETRIEVE_MSG
    )
    chat_history = "\n".join([f"{'User' if msg.is_user else 'Bot'}: {msg.text}" for msg in messages])
    
    chain = self.prompt | self.model
  
    return chain.invoke({"chat_history": chat_history, "user_query": text}), self.AGENT_TYPE

    