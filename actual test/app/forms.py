from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Regexp, ValidationError, Email, Length, EqualTo
from app import db 


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')


def name_exists(form, givenname):
	if db.users.find({'username':givenname}).count() != 0:
		raise ValidationError('User with that name already exists.')
		
def email_exists(form, givenemail):
	if db.users.find({'email':givenemail}).count() != 0:
		raise ValidationError('User with that email already exists.')
		
class Registerform(Form):
	username = StringField(
		'Username',
		"""validators = [DataRequired(),
					  Regexp(
						r'^[a-zA-Z0-9]+$',
						message = ("Username can allow upper, lower case and numbers.")
					  ),
					  name_exists
					  ]"""
	)
	email = StringField(
		'Email',
		"""validators = [DataRequired(),
					  Email(),
					  email_exists
					  ]"""
	)
	password = PasswordField(
		'Password',
		"""validators = [DataRequired(),
					  Length(min=2),
					  EqualTo('password2', message='Passwords must match.')
					  ]"""
	)
	password2 = PasswordField(
		'Confirm Password',
		"""validators = [DataRequired()]"""
	)