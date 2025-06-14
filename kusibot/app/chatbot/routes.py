from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from kusibot.services import chatbot_service

chatbot_bp = Blueprint('chatbot_bp', __name__, template_folder='templates', static_folder='static')

@chatbot_bp.route('/', methods=['GET'])
@login_required
def chatbot():
    """Render the chatbot interface. Requires user to be logged in."""

    # Gets the current conversation (last until session expires aka logs out)
    # or Creates a new one
    convo = chatbot_service.create_or_get_conversation(current_user.id)
    return render_template('chatbot.html', conversation=convo)

@chatbot_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle user messages and return the chatbot responses."""

    # Get the message from the request
    data = request.json
    user_message = data.get('message', '')
    
    # If no user message, respond with a simple message.
    if not user_message:
        return jsonify({'response': chatbot_service.CHATBOT_NO_MSG_PROVIDED})
        
    # Return chatbot response as JSON
    return jsonify({
        'response': chatbot_service.get_response(user_message, current_user.id)
    })