from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user

#########################################
# Handling chatbot interactions kusibot kusibot123
#########################################

chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/', methods=['GET'])
@login_required
def chatbot():
    return render_template('chatbot.html')

@chatbot_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    # Get the message from the request
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get response from chatbot
    response = current_app.chatbot.get_response(user_message, current_user.id)
    
    # Return response
    return jsonify({'response': response})