from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, TextAreaField,
    SelectField, IntegerField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
)
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is already registered. '
                'Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class IssueForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=[
            ('Health', 'Health'),
            ('Education', 'Education'),
            ('Sanitation', 'Sanitation'),
            ('Women’s Safety', 'Women’s Safety'),
            ('Technology', 'Rural Tech Access'),
            ('Environment', 'Environment')
        ],
        validators=[DataRequired()])
    total_slots = IntegerField(
        'Total Available Slots',
        validators=[DataRequired(), NumberRange(min=1)])
    mode = StringField('Mode (e.g., Online, Pune)',
                       validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Post Issue')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')