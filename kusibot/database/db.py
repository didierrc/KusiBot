from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

#########################################
# SQLAlchemy DB initialization
#########################################

# Creating SQLALchemy instance
db = SQLAlchemy()

# Creating Migrate instance
migrate = Migrate()

def init_db(app):
    """
    Initialising DB (SQLAlchemy) with Flask app.
    
    Parameters:
        app: The Flask app instance.
    """

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Initialize Flask-migrate: Useful when developing for DB SCHEMA CHANGES.
    migrate.init_app(app, db, directory='kusibot/database/migrations')

    # Creating tables and Professional User
    initialise_data(app, db)
    
def initialise_data(app,db):
    """
    Initialises the database creating all its tables and the UNIQUE professional user who has access
    to the non-professional users conversations and insights.

    Parameters:
        app: The Flask app instance.
        db: The SQLAlchemy instance.
    """

    with app.app_context():

        db.create_all()
        
        # Create a professional user if not exists
        from kusibot.database.db_repositories import UserRepository
        user_repo = UserRepository()

        professional_username = os.environ["PROFESSIONAL_USERNAME"]
        professional_password = os.environ["PROFESSIONAL_PASSWORD"]
        professional_email = os.getenv("PROFESSIONAL_EMAIL", "pro@kusibot.com")
        
        user = user_repo.get_user_by_username(professional_username)
        if not user:
            from app import bcrypt
            professional_password = bcrypt.generate_password_hash(professional_password).decode('utf-8')
            user_repo.add_user(professional_username, professional_email, professional_password, is_professional=True)
            print(f"Professional user {professional_username} created.")