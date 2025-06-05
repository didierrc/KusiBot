from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from kusibot.services import (
    DashboardService
) 

professional_bp = Blueprint('professional_bp', __name__, template_folder='templates', static_folder='static')
dashboard_service = DashboardService()

@professional_bp.route('/')
@login_required
def dashboard():
    """Render the dashboard page (protected) with the list of users using KusiBot."""
    users = dashboard_service.get_chat_users()
    return render_template('dashboard.html', users=users)

@professional_bp.route('/conversations')
@login_required
def dashboard_conversations():
    """Get the conversation for a selected user (URL parameter)."""

    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400
    
    response = dashboard_service.get_conversation_for_user(user_id)
    return jsonify(response)

@professional_bp.route('/assessments')
@login_required
def dashboard_assessments():
    """Get the assessments for a selected user (URL parameter)."""
    
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400
    
    response = dashboard_service.get_assessments_for_user(user_id)
    return jsonify(response)


