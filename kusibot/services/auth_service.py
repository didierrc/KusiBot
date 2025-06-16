from kusibot.database.db_repositories import UserRepository
import re

class AuthService:
    """
    Service class for handling user authentication and registration.
    """

    def __init__(self):
        """
        Initialises the AuthService class with their needed repositories.
        """

        self.user_repository = UserRepository()

    def possible_login(self, identifier, password):
        """
        Logs in a user with the given identifier and password.

        Parameters:
            identifier (str): The username or email of the user.
            password (str): The password of the user.
        Returns:
            User: The authenticated user object if login is successful, otherwise None.
        """

        # Check first whether the identifier is an email or username.
        if re.match(r'[^@]+@[^@]+\.[^@]+', identifier):
            user = self.user_repository.get_user_by_email(identifier)
        else:
            user = self.user_repository.get_user_by_username(identifier)

        # Check if user exists and password is correct.        
        if user and user.check_password(password):
            return user
        return None

    def register(self, username, email, password, is_professional=False):
        """
        Registers a new user in KusiBot.
        
        Parameters:
            username (str): The username of the new user.
            email (str): The email of the new user.
            password (str): The password of the new user.
            is_professional (bool): Whether the user is a professional user or not.
        
        """

        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = self.user_repository.add_user(username, 
                                             email, 
                                             hashed_password, 
                                             is_professional)
    
        return True if user else False
        