from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from kusibot.app.auth.forms import RegisterForm, LoginForm
from kusibot.app.auth.utils import redirect_to_principal_page
from kusibot.services import (
    AuthService,
    ChatbotService
)

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates', static_folder='static')
auth_service = AuthService()
chatbot_service = ChatbotService()

MESSAGES = {
    'invalid_login': 'Invalid username or password.',
    'registration_success': 'Registration successful! You can now log in.',
    'registration_error': 'An error occurred during registration. Please try again.'
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route for KusiBot. Accepts the following methods:
    - GET: Goes to principal page if authenticated, else, goes to Login Page.
    - POST: Log in a user to Kusibot given its username and password.
    """

    # If user is already authenticated, redirect to principal page
    if current_user.is_authenticated:
        return redirect_to_principal_page(current_user.is_professional)
    
    # If user is not authenticated, create login form object.
    form = LoginForm()
    
    # If form is submitted, validate the form data.
    if form.validate_on_submit():

        user = auth_service.possible_login(form.username.data, 
                                           form.password.data)

        if user:
            login_user(user, remember=form.remember.data)
            return redirect_to_principal_page(user.is_professional)
        else:
            flash(MESSAGES["invalid_login"], "error")
        
    # If form is not submitted, render login page.
    return render_template("login.html", form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Register route for KusiBot. Accepts the following methods:
    - GET: Goes to principal page if authenticated, else, goes to Register Page.
    - POST: Register a new user in KusiBot.
    """

    # If user is already authenticated, redirect to principal page
    if current_user.is_authenticated:
        return redirect_to_principal_page(current_user.is_professional)
    
    # If user is not authenticated, create register form object.
    form = RegisterForm()
    
    # If form is submitted, validate the form data.
    if form.validate_on_submit():
    
        # Register a USER (not a professional)
        success_register = auth_service.register(form.username.data, 
                                                 form.email.data, 
                                                 form.password.data)

        if success_register:
            flash(MESSAGES["registration_success"], "success")
            
            from app import LOGIN_URL
            return redirect(url_for(LOGIN_URL))
        else:
            flash(MESSAGES["registration_error"], "error")

    # If form is not submitted, render signup page.
    return render_template("signup.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """
    Logs out an authenticated user from KusiBot. Accepts the following methods:
    - GET: Logs out, ends any current conversation and returns to Main Page.
    """

    chatbot_service.end_conversation(current_user.id)
    logout_user()

    from app import MAIN_URL
    return redirect(url_for(MAIN_URL))
