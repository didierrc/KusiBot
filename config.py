import os, pathlib

#####################################################################
# Different configurations for the app                              #
# https://dev.to/hackersandslackers/configuring-your-flask-app-2246 #
#####################################################################

# Get the base directory of the current project.
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DEFAULT_SQL = f'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'kusibot.db')

class Config:
    """Base configuration class for the Flask app."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable the logs of INSERT, UPDATE, DELETE operations. Too much overhead.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_SQL)


class DevelopmentConfig(Config):
    """Development configuration for the Flask app."""
    
    DEBUG = True # The server will automatically reload when code changes. Show errors in the browser.

class TestingConfig(Config):
    """Testing configuration for the Flask app."""
    
    TESTING = True # Exceptions are propagated rather than handled by the the app’s error handlers.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # In memory DB.
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration for the Flask app."""
    
    DEBUG = False # No reload, no errors in the browser.

# Dictionary to map the configuration name to the configuration object.
config = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
