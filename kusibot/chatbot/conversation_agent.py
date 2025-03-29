from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

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
- BERT Intent Detected: {intent}
- Previous Conversation History: {chat_history}
- User Query: {user_query}

# Response Guidelines:
- Respond with empathy and understanding
- Avoid giving direct medical advice
- Encourage professional help when needed
- Maintain a calm and supportive tone
- If the conversation suggests serious mental health concerns, 
  gently suggest speaking with a mental health professional.

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
    except Exception:
      print("ERROR: OLLAMA IS NOT INSTALLED")
      self.model = ""
    
    self.prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
  def generate_response(self, text, intent,  user_id):
    
    if self.model:
      chain = self.prompt | self.model
      return chain.invoke({"intent": intent, "chat_history": "", "user_query": text})
    else:
      return "Bot: Sorry, Ollama is not installed and I'm not able to help you."

    