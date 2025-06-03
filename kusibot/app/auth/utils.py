from flask import redirect, url_for

def redirect_to_principal_page(is_professional):
    """
    Redirects the authenticated current user to its corresponding
    principal page.
    
    - USER: Goes to /chatbot
    - PROFESSIONAL: Goes to /internal/dashboard
    
    Parameters:
        is_professional (bool): Indicates if the user is a professional or not.
    Returns:
        Response: Redirect response to the user's principal page.
    """

    from app import CHATBOT_URL, DASHBOARD_URL
    if is_professional:
        return redirect(url_for(DASHBOARD_URL))
    return redirect(url_for(CHATBOT_URL))