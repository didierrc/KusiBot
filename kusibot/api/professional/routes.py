from flask import Blueprint, render_template, current_app, jsonify, request
from flask_login import login_required

#########################################
# Handling professional related routes  #
#########################################

professional_bp = Blueprint('professional_bp', __name__)

@professional_bp.route('/')
@login_required
def dashboard():
    users = current_app.dashboard.get_chat_users()
    return render_template('dashboard.html', users=users)

@professional_bp.route('/conversations')
@login_required
def dashboard_conversations():
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400
    

    response = current_app.dashboard.get_conversation_for_user(user_id)
    return jsonify(response)

@professional_bp.route('/assessments')
@login_required
def dashboard_assessments():
    
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400
    
    response = current_app.dashboard.get_assessments_for_user(user_id)
    return jsonify(response)


