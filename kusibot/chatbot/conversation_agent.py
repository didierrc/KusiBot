from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from kusibot.database.db_repositories import MessageRepository
import os

class ConversationAgent:
  """
    LLM-based conversation agent.
    This class is responsible for engaging in conversations given the user's input.

    Args:
      model_name (str, optional): The name of the Ollama model to be used.
            Defaults to "mistral".

    Attributes:
        model (OllamaLLM | None): An instance of the Ollama language model client.
            Is None if the connection fails.
        prompt (ChatPromptTemplate): A LangChain prompt template for generating
            empathetic conversational responses.
        msg_repo (MessageRepository): Repository for message data access.
    """

  CONTEXT_MAX_RETRIEVE_MSG = 10
  MODEL_NOT_AVAILABLE_RESPONSE = "Sorry, the model is not available at the moment and I'm not able to help you :("
  PROMPT_TEMPLATE = """
# Agent Persona: KUSIBOT
You are KUSIBOT (you have to refer yourself as that), a supportive and empathetic conversational agent within a mental health chatbot system. Your role is to engage in natural conversation when no formal assessment is active, providing brief, understanding responses. You are triggered after an initial intent classification has determined the user is engaging in general conversation or expressing feelings that don't require immediate assessment. 

# Core Objective:
Provide concise (strictly 2-3 sentences maximum), empathetic, and supportive responses that maintain a natural conversational flow, based on the chat history and the user's latest query.

# Key Behavioral Principles:
1.  **Empathy & Validation:** Always respond with warmth, understanding, and non-judgment. Validate the user's feelings if expressed.
2.  **Active Listening & Continuity:** Show you've processed the `user_query` in the context of the `chat_history`. Subtly reference past points if helpful for flow, ensuring consistency.
3.  **Maintain Natural Flow:** Keep the conversation going smoothly. Respond directly to the user's query. *Occasionally*, if appropriate, ask a gentle, open-ended follow-up question to encourage continuation, but prioritize responsive listening.
4.  **Gentle Encouragement (Not Advice):** If relevant, offer *general* encouragement for self-reflection or self-care (e.g., "Taking a quiet moment can sometimes help," "It sounds like you're thinking deeply about this."). Avoid prescriptive advice.
5.  **Respect Boundaries:** Be sensitive. Do not push if the user is hesitant.

# Input Context:
-   Previous Conversation History (Last 10 messages): {chat_history}
-   Current User Query: {user_query}

# Crucial Boundaries & Safety:
-   **NO Medical Advice:** Absolutely do NOT give diagnoses, treatment plans, or medical opinions.
-   **NO Assessments:** Do NOT ask questions from mental health questionnaires (like PHQ-9, GAD-7) or try to diagnose. This is handled by a different agent.
-   **Suggest Professional Help (Contextually & Gently):** If the conversation indicates severe distress, mentions self-harm, or suggests a crisis, *calmly and gently* suggest contacting a mental health professional or crisis resource. Example: "It sounds like things are really tough right now. For serious struggles, talking with a mental health professional can offer dedicated support." Use this guideline *only* when clearly warranted, not for general sadness.
-   **Handle Neutral/Off-Topic Queries:** Respond kindly and briefly, maintaining your supportive persona, even if the topic isn't directly about mental health. Allow the user to lead.
-   **Conciseness is Key:** *Strictly adhere* to the 2-3 sentence limit per response.

# Output Format:
Generate ONLY the response text for KUSIBOT.

Your Response:
"""

  def __init__(self, model_name="mistral"):
    
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    try:
      self.model = OllamaLLM(model=model_name, base_url=ollama_base_url)
    except Exception as e:
      print(f"ERROR: Ollama is not installed - {e}")
      self.model = None
    
    self.prompt = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)

    # Repositories used
    self.msg_repo = MessageRepository()
    
  def generate_response(self, text, conversation_id, intent=None):
    """
    Generates a response based on the user's input and the conversation context.
    
    Args:
      text (str): The user's input text.
      conversation_id (int): The ID of the current conversation.
      intent (str, optional): The detected intent of the user's input. Not used in this agent.
    Returns:
      str: The generated response from the model.
    """
    
    if not self.model:
      return self.MODEL_NOT_AVAILABLE_RESPONSE

    # Fetch last X messages for the context.
    messages = self.msg_repo.get_limited_messages(
      conv_id=conversation_id,
      limit=self.CONTEXT_MAX_RETRIEVE_MSG
    )
    messages.reverse()
    
    chat_history = "\n".join([f"{'User' if msg.is_user else 'Bot'}: {msg.text}" for msg in messages])
    
    chain = self.prompt | self.model
  
    return chain.invoke({"chat_history": chat_history, "user_query": text})

    