from flask import Blueprint, render_template
from flask_login import login_required

#########################################
# Handling chatbot interactions
#########################################

chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/', methods=['GET'])
@login_required
def chatbot():
    return render_template('chatbot.html')