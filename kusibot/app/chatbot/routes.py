from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from kusibot.services import chatbot_service
from kusibot.app.auth.utils import standard_user_required

chatbot_bp = Blueprint('chatbot_bp', __name__, template_folder='templates', static_folder='static')

CHAT_ERROR_MSG = "An error occurred. Sorry for the inconvenience :("

@chatbot_bp.route('/', methods=['GET'])
@login_required
@standard_user_required
def chatbot():
    """Render the chatbot interface. Requires user to be logged in.
    
    Returns:
        str: The chatbot HTML page to render.
    """

    # Gets the current conversation (last until session expires aka logs out)
    # or Creates a new one
    convo = chatbot_service.create_or_get_conversation(current_user.id)
    return render_template('chatbot.html', conversation=convo)

@chatbot_bp.route('/chat', methods=['POST'])
@login_required
@standard_user_required
def chat():
    """Handle user messages and return the chatbot responses.
    
    Returns:
        Response: The JSON response message from the chatbot.
    """

    try:
        # Get the message from the request
        data = request.json
        user_message = data.get('message', '')
    
        # If no user message, respond with a simple message.
        if not user_message:
            return jsonify({'response': chatbot_service.CHATBOT_NO_MSG_PROVIDED})
        
        # Return chatbot response as JSON
        bot_response = chatbot_service.get_response(user_message, current_user.id)
        return jsonify({
            'response': bot_response["agent_response"],
            'agent_type': bot_response["agent_type"],
            'intent': bot_response["intent_detected"]
        })
    
    except Exception:
        return jsonify({
            'response': CHAT_ERROR_MSG,
            'agent_type': None,
            'intent': None
        }), 500