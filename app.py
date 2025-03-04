from flask import Flask
from flask_wtf.csrf import CSRFProtect
from kusibot.config import config
from kusibot.database.db import init_db
from kusibot.api.main.routes import main_bp
from kusibot.api.auth.routes import auth_bp
from kusibot.api.chatbot.routes import chatbot_bp
from dotenv import load_dotenv
import os

#########################################
# Main entry point for the application.
#########################################

load_dotenv()

def create_app(config_name='default'):
  """Application-factory pattern"""

  # Selecting Flask configuration
  app_config = config[config_name]

  # Creating Flask instance
  app = Flask(__name__,
            template_folder='kusibot/api/frontend/templates',
            static_folder='kusibot/api/frontend/static')
  
  # Load configuration
  app.config.from_object(app_config)

  # Setting CSRF protection
  CSRFProtect(app)

  # Initialise database
  init_db(app)

  # Registering the blueprints
  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp, url_prefix='/auth')
  app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

  return app


def main():
  """Main entry point for running the app."""

  app = create_app(os.environ.get('FLASK_ENV', 'default'))
  app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == '__main__':
  main()  