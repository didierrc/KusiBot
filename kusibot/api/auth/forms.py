from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from kusibot.database.models import User

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', 
                           validators=[DataRequired()], 
                           render_kw={'placeholder': 'KusiBot'})
    password = PasswordField('Password', 
                             validators=[DataRequired()],
                             render_kw={'placeholder': 'MySuperPassword'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=30)],
                           render_kw={'placeholder': 'KusiBot'})
    email = StringField('Email', 
                        validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'kusibot@email.com'})
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6, max=20)],
                             render_kw={'placeholder': 'MySuperPassword'})
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={'placeholder': 'MySuperPassword'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')