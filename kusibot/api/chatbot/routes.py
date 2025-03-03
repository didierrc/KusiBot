from flask import Blueprint, render_template

#########################################
# Handling chatbot interactions
#########################################

chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/', methods=['GET'])
def chatbot():
    return render_template('chatbot.html')