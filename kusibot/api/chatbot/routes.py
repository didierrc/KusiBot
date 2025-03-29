from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user

#########################################
# Handling chatbot interactions kusibot kusibot123
#########################################

chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/', methods=['GET'])
@login_required
def chatbot():
    """Render the chatbot interface"""

    # Gets the current conversation (last until session expires aka logs out)
    # or Creates a new one
    convo = current_app.chatbot.create_or_get_conversation(current_user.id)
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
        return jsonify({'response': 'Sorry, but you didn\'t provide any message.'})
    
    # Get response from chatbot
    response = current_app.chatbot.get_response(user_message, current_user.id)
    
    # Return chatbot response as JSON
    return jsonify({'response': response})