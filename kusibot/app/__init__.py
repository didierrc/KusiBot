from .general.routes import main_bp
from .auth.routes import auth_bp
from .chatbot.routes import chatbot_bp
from .dashboard.routes import professional_bp

__all__ = [
    "main_bp",
    "auth_bp",
    "chatbot_bp",
    "professional_bp",
]