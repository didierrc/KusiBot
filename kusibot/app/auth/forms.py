from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from kusibot.database.models import User

class LoginForm(FlaskForm):
    """Login form."""
    identifier = StringField('Username or Email', 
                             validators=[DataRequired(), Length(min=4, max=64)], 
                             render_kw={'placeholder': 'kusibot or kusibot@email.com'})
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=8, max=64)],
                             render_kw={'placeholder': 'MySuperPassword'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Registration form."""
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
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')