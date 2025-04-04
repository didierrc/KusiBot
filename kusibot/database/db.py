from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
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
        app (Flask): The Flask app instance.
    """

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Initialize Flask-migrate: Useful when developing for DB changes.
    migrate.init_app(app, db, directory='kusibot/database/migrations')

    # Creating tables and data needed for the application: Professional User and Questionnaires data
    db.create_all()
    create_professional_user(app, db)
    
def create_professional_user(app,db):
    with app.app_context():
        
        # Create a professional user if not exists
        from kusibot.database.models import User
        professional_username = os.environ["PROFESSIONAL_USERNAME"]
        user = User.query.filter_by(username=professional_username).first()
        if not user:
            hashed_password = Bcrypt().generate_password_hash(os.environ["PROFESSIONAL_PASSWORD"]).decode('utf-8')
            user = User(username=professional_username, 
                        email=os.getenv("PROFESSIONAL_EMAIL", "pro@kusibot.com"), 
                        password=hashed_password,
                        is_professional=True)
        
            db.session.add(user)
            db.session.commit()