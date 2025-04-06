from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from kusibot.api.auth.forms import RegisterForm, LoginForm
from kusibot.database.db_repositories import UserRepository
from kusibot.api.auth.utils import redirect_to_principal_page

#########################################
# Handling user authentication
#########################################

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

ERROR_MESSAGES = {
    'invalid_login': 'Invalid username or password.',
}

CHATBOT_URL = "chatbot_bp.chatbot"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route for the application.Accepts the following methods:
    - GET: Goes to principal page if authenticated, else, goes to Login.
    - POST: Log in a user to Kusibot given its username and password.
    """

    # If user is already authenticated, redirect to principal page
    if current_user.is_authenticated:
        return redirect_to_principal_page(current_user.is_professional)
    
    # If user is not authenticated, create login form object.
    form = LoginForm()
    
    # If form is submitted, validate the form data.
    if form.validate_on_submit():
        
        # Check if user exists and password is correct.
        user_repo = UserRepository()
        user = user_repo.get_user_by_username(form.username.data)
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect_to_principal_page(user.is_professional)
        else:
            flash(ERROR_MESSAGES['invalid_login'], "error")
    
    # If form is not submitted, render login page.
    return render_template("login.html", form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def register():
    """Register route for the application."""

    # If user is already authenticated, redirect to chatbot.
    if current_user.is_authenticated:
        return redirect(url_for(CHATBOT_URL))
    
    # If user is not authenticated, create register form object.
    form = RegisterForm()
    
    # If form is submitted, validate the form data.
    if form.validate_on_submit():
    
        user_repo = UserRepository()
        user_repo.add_user(form.username.data, form.email.data, form.password.data, is_professional=False)
    
        # Redirect to login page.
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth_bp.login'))

    # If form is not submitted, render signup page.
    return render_template('signup.html', form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """Logout route for the application."""

    current_app.chatbot.end_conversation(current_user.id)
    logout_user()
    return redirect(url_for("main_bp.index"))
