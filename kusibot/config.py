import os, pathlib

#########################################
# Diffrerent configurations for the app #
# https://dev.to/hackersandslackers/configuring-your-flask-app-2246 #
#########################################

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable the logs of INSERT, UPDATE, DELETE operations. Too much overhead.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR}/instance/kusibot.db'
    )


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True # The server will automatically reload when code changes. Show errors in the browser.

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True # Exceptions are propagated rather than handled by the the app’s error handlers.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # In memory DB.


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
