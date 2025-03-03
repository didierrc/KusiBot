from flask import Flask
from flask_wtf.csrf import CSRFProtect
from kusibot.api.main.routes import main_bp
from kusibot.api.auth.routes import auth_bp
from kusibot.api.chatbot.routes import chatbot_bp

#########################################
# Main entry point for the application.
#########################################

app = Flask(__name__,
            template_folder='kusibot/api/frontend/templates',
            static_folder='kusibot/api/frontend/static')

# Setting CSRF protection
app.config['SECRET_KEY'] = 'MY_SECRET_KEY'
csrf = CSRFProtect(app)

# Registering the blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')


def main():
    """Main entry point for running the app."""
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == '__main__':
  main()  