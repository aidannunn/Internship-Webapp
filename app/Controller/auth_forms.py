from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Length,Email
from wtforms.widgets import ListWidget, CheckboxInput
from app.Model.models import User, Field, Language, Elective

def get_languages():
    return Language.query.all()
def getLanguageLabel(theLanguage):
    return theLanguage.name

def get_electives():
    return Elective.query.all()
def getElectiveLabel(theElective):
    return theElective.title

def get_fields():
    return Field.query.all()
def getFieldLabel(theField):
    return theField.name

class StudentRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    WSU_id = StringField('WSU_id', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    gpa = StringField('GPA', validators=[DataRequired()])
    completed_courses = QuerySelectMultipleField('Completed courses:', query_factory=get_electives, get_label= getElectiveLabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    interested_fields = QuerySelectMultipleField('Interested fields: ', query_factory=get_fields, get_label= getFieldLabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    known_languages = QuerySelectMultipleField('Known programming languages: ', query_factory=get_languages, get_label= getLanguageLabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    prior_research_experience = StringField('Prior Research Experience', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username already exists! Please use a different username.')
    
    def validate_WSU_id(self, WSU_id):
        user = User.query.filter_by(WSU_id=WSU_id.data).first()
        if user is not None:
            raise ValidationError('The ID already exists! Please use a different ID.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email is already in use! Please use a different email address.')

class FacultyRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    WSU_id = StringField('WSU ID', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username already exists! Please use a different username.')

    def validate_WSU_id(self, WSU_id):
        user = User.query.filter_by(WSU_id=WSU_id.data).first()
        if user is not None:
            raise ValidationError('The ID already exists! Please use a different ID.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email is already in use! Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')