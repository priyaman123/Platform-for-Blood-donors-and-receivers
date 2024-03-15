from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, IntegerField, validators, SelectField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from donors.models import User, Post
from flask_login import current_user
class RegistrationForm (FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=5, max=10)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	list_blood = SelectField('BLOODGROUP',choices=[('o negative', 'O(-ve)'),('o possitve', 'O(+ve)'),('b possitive', 'B(+ve)'), ('b negative','B(-ve)'), ('a possitive','A(+ve)'),('a1 possitive','A1(+ve)'),('a1 negative','A1(-ve)'),('a negative', 'A(-ve)')])
	phonenumber = IntegerField('Phonenumber', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign up')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('email already exist')
	def validate_phonenumber(self, phonenumber):
		usernum = User.query.filter_by(phonenumber=phonenumber.data).first()
		if usernum:
			raise ValidationError('phonenumber already exist')



class LoginForm (FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')



class UpdateAccountForm (FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=5, max=10)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	list_blood = SelectField('BLOODGROUP',choices=[('o negative', 'O(-ve)'),('o possitve', 'O(+ve)'),('b possitive', 'B(+ve)'), ('b negative','B(-ve)'), ('a possitive','A(+ve)'),('a1 possitive','A1(+ve)'),('a1 negative','A1(-ve)'),('a negative', 'A(-ve)')])
	phonenumber = IntegerField('Phonenumber', validators=[DataRequired()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['png', 'jpg'])])
	submit = SubmitField('Update')


	

class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Post')

class NeedBlood(FlaskForm):
	hospital = StringField('Hospital Address', validators=[DataRequired()])
	list_blood = SelectField('BLOODGROUP',choices=[('o negative', 'O(-ve)'),('o possitve', 'O(+ve)'),('b possitive', 'B(+ve)'), ('b negative','B(-ve)'), ('a possitive','A(+ve)'),('a1 possitive','A1(+ve)'),('a1 negative','A1(-ve)'),('a negative', 'A(-ve)')])
	submit = SubmitField('Post')

