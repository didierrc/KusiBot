from flask import Blueprint, render_template
from flask_login import login_required

#########################################
# Handling professional related routes  #
#########################################

professional_bp = Blueprint('professional_bp', __name__)

@professional_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')



