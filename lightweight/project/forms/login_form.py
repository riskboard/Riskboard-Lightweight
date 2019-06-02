from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8,max=30)])
  submit = SubmitField('Sign In')