from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

    # Creating tables
    with app.app_context():
        db.create_all()