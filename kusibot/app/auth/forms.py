from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from kusibot.database.models import User

class LoginForm(FlaskForm):
    """
    Login form for user authentication.

    This form is used in the login view to collect and validate user
    credentials. It includes fields for an identifier (username or email),
    a password, an option to remember the session, and a submit button.

    Attributes:
        identifier (StringField): A required text field for the user's
            username or email. Validates for a length between 4 and 64
            characters.
        password (PasswordField): A required password field. Validates for
            a length between 8 and 64 characters.
        remember (BooleanField): An optional checkbox to enable a persistent
            user session.
        submit (SubmitField): The form submission button.
    """

    identifier = StringField('Username or Email', 
                             validators=[DataRequired(), Length(min=4, max=64)], 
                             render_kw={'placeholder': 'kusibot or kusibot@email.com'})
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=8, max=64)],
                             render_kw={'placeholder': 'MySuperPassword'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """
    Registration form for new user creation.

    This form is used in the registration view to collect and validate
    information for a new standard user account. It includes fields for
    username, email, and password, with strong password validation and
    confirmation. Custom validators are used to check for the uniqueness
    of the username and email against the database.

    Attributes:
        username (StringField): A required text field for the new user's
            username. Validates for a length between 4 and 20 characters.
        email (StringField): A required text field for the user's email
            address. Validates for a valid email format.
        password (PasswordField): A required password field with complex
            validation rules, including length, and the required presence of
            uppercase, lowercase, numeric, and special characters.
        confirm_password (PasswordField): A required password confirmation
            field that must be equal to the password field.
        submit (SubmitField): The form submission button.
    """
    
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'kusibot'})
    email = StringField('Email', 
                        validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'kusibot@email.com'})
    password = PasswordField('Password', 
                             validators=[DataRequired(), 
                                         Length(min=8, max=64, message='Password must be between 8 and 64 characters.'),
                                         Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#?!@$%^&*-])[A-Za-z\d#?!@$%^&*-]{8,}$',
                                                message='Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')],
                             render_kw={'placeholder': 'my5up€rPWD'})
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={'placeholder': 'my5up€rPWD'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        Validation function that check the uniqueness of the username 
        in the registration form.

        Args:
            username (str): The username input of the unregistered user.
          
        Raises:
            ValidationError: If the username is already taken.
        
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
        
    def validate_email(self, email):
        """
        Validation function that check the uniqueness of the email 
        in the registration form.
        
        Args:
            email (str): The email input of the unregistered user.
          
        Raises:
            ValidationError: If the username is already taken.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')