from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user

def redirect_to_principal_page(is_professional):
    """
    Redirects the authenticated current user to its corresponding
    principal page.
    
    - USER: Goes to /chatbot
    - PROFESSIONAL: Goes to /internal/dashboard
    
    Args:
        is_professional (bool): Indicates if the user is a professional or not.
    Returns:
        Response: Redirect response to the user's principal page.
    """

    from app import CHATBOT_URL, DASHBOARD_URL
    if is_professional:
        return redirect(url_for(DASHBOARD_URL))
    return redirect(url_for(CHATBOT_URL))

# https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/
def standard_user_required(f):
    """
    A decorator function to ensure standard users have access to
    the allowed views. If user is not standard, it aborts with a 403
    Forbidden error.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_professional:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
