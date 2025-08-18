from flask import Blueprint, render_template, jsonify, request, flash
from flask_login import login_required
from kusibot.services import (
    DashboardService
)
from kusibot.app.auth.utils import professional_user_required

professional_bp = Blueprint('professional_bp', __name__, template_folder='templates', static_folder='static')
dashboard_service = DashboardService()

DB_USER_ERROR_FETCH = "There was an error while fetching the users. Try again later."

@professional_bp.route('/')
@login_required
@professional_user_required
def dashboard():
    """Render the dashboard page (protected) with the list of users using KusiBot.
    
    Returns:
        str: The HTML dashboard page to render.
    """

    try:
        users = dashboard_service.get_chat_users()
        return render_template('dashboard.html', users=users)
    except Exception:
        flash(DB_USER_ERROR_FETCH, "error")
        return render_template('dashboard.html', users=[])

@professional_bp.route('/conversations')
@login_required
@professional_user_required
def dashboard_conversations():
    """Get the conversations history for a selected user (URL parameter).
    
    Returns:
        Response: The JSON conversations for the given user.
    """

    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400
    
    response = dashboard_service.get_conversations_for_user(user_id)
    return jsonify(response)

@professional_bp.route('/conversation_messages')
@login_required
@professional_user_required
def dashboard_conversation_messages():
    """Get the conversation messages for a specific conversation ID (URL parameter).
    
    Returns:
        Response: The JSON details of the specified conversation.
    """
    
    conversation_id = request.args.get('conversation_id', type=int)
    if conversation_id is None:
        return jsonify({'error': 'conversation_id is required'}), 400

    response = dashboard_service.get_conversation_messages(conversation_id)
    return jsonify(response)

@professional_bp.route('/assessments')
@login_required
@professional_user_required
def dashboard_assessments():
    """Get the assessments for a selected user (URL parameter).
    
    Returns:
        Response: The JSON assessments for the given user.
    """
    
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400
    
    response = dashboard_service.get_assessments_for_user(user_id)
    return jsonify(response)


