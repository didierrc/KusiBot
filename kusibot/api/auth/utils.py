from flask import redirect, url_for

CHATBOT_URL = "chatbot_bp.chatbot"
DASHBOARD_URL = "professional_bp.dashboard"

def redirect_to_principal_page(is_professional: bool):
    """
    Redirects the current user (authenticated) to its corresponding
    principal page.
    
    - USER: Goes to /chatbot
    - PROFESSIONAL: Goes to /internal/dashboard
    
    ## Parameters
    is_professional: bool -> True if the user is a professional. False otherwise. 
    """

    if is_professional:
        return redirect(url_for(DASHBOARD_URL))
    return redirect(url_for(CHATBOT_URL))