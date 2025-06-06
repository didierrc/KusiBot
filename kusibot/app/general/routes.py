from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__, template_folder='templates', static_folder='static')

@main_bp.route('/')
def index():
    """Render the initial page"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@main_bp.route('/sos')
def sos():
    """Render the chatbot SOS list page"""
    return render_template('sos.html')