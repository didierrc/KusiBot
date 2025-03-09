from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from kusibot.api.auth.forms import RegisterForm, LoginForm
from kusibot.database.models import User
from kusibot.database.db import db

#########################################
# Handling user authentication
#########################################

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("chatbot_bp.chatbot"))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            
            login_user(user, remember=form.remember.data)
            return redirect(url_for("chatbot_bp.chatbot"))
        else:
            print("Invalid username or password")
    
    return render_template("login.html", form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("chatbot_bp.chatbot"))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, 
                        email=form.email.data, 
                        password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth_bp.login'))
    
    return render_template('signup.html', form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_bp.index"))
