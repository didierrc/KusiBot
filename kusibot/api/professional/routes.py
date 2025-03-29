from flask import Blueprint, render_template

#########################################
# Handling professional related routes  #
#########################################

professional_bp = Blueprint('professional_bp', __name__)

@professional_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



