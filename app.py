from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import render_template
from kusibot.database.models import User
from config import config
from kusibot.database.db import init_db
from kusibot.api.main.routes import main_bp
from kusibot.api.auth.routes import auth_bp
from kusibot.api.chatbot.routes import chatbot_bp
from kusibot.api.professional.routes import professional_bp
from kusibot.chatbot.chatbot import Chatbot
from kusibot.dashboard.dashboard import Dashboard
from dotenv import load_dotenv
import os

##############################################
# Main entry point for the whole application #
##############################################

# Load environment variables from .env file.
load_dotenv()

# Initialise Bcrypt module for encryption.
bcrypt = Bcrypt()

CHATBOT_URL = "chatbot_bp.chatbot"
DASHBOARD_URL = "professional_bp.dashboard"
LOGIN_URL = "auth_bp.login"
MAIN_URL = "main_bp.index"

def create_app(config_name):
  """
  Creates and Configures a Flask app instance
  following the Application-factory pattern.
  
  Parameters:
    config_name (str): The configuration name to use [dev/testing/prod].
  
  Returns:
    Flask: The Flask app instance.
  """

  # Selecting corresponding Flask configuration object.
  app_config = config[config_name]

  # Creating Flask instance with common templates and static folders.
  app = Flask(__name__,
            template_folder='kusibot/api/frontend/templates',
            static_folder='kusibot/api/frontend/static')
  
  # Load selected configuration object to the Flask app.
  app.config.from_object(app_config)

  # Setting CSRF protection
  CSRFProtect(app)

  # Initialize Bcrypt with the Flask app.
  bcrypt.init_app(app)

  # Initialise database to use with the Flask app (db route depends on the config).
  init_db(app)

  # Setting up login manager and login page for the Flask app.
  login_manager = LoginManager(app)
  login_manager.login_view = 'auth_bp.login'

  # Define the function that will be called to load a user.
  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(int(user_id))
  
  # Setting up logic instances.
  app.chatbot = Chatbot()
  app.dashboard = Dashboard()

  # Registering the blueprints routes for the Flask app.
  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp, url_prefix='/auth')
  app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
  app.register_blueprint(professional_bp, url_prefix='/dashboard')

  @app.errorhandler(404)
  def page_not_found(e):
    """Custom error handler for 404 errors."""
    return render_template('not_found.html'), 404

  return app

def main():
  """Main entry point for running the app using Flask server."""
  app = create_app(os.getenv('FLASK_ENV', 'default'))
  app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == '__main__':
  main()  