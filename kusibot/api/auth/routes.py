from flask import Blueprint, render_template

#########################################
# Handling user authentication
#########################################

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET'])
def get_login():
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET'])
def get_signup():
    return render_template('signup.html')

