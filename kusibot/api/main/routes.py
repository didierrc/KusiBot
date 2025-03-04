from flask import Blueprint, render_template

#########################################
# Handling general routes
# https://flask.palletsprojects.com/en/stable/blueprints/
#########################################

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

