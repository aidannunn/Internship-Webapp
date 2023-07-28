from flask_wtf import FlaskForm
from datetime import date
from wtforms import StringField, SubmitField, SelectField, TextAreaField, BooleanField, PasswordField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import DateTimeField
from app.Model.models import User, Field, Language, Elective, Post

def get_all_fields():
    return Field.query.all()

def get_fieldlabel(theField):
    return theField.name

def get_languages():
    return Language.query.all()

def getLanguageLabel(theLanguage):
    return theLanguage.name

def get_electives():
    return Elective.query.all()

def getElectiveLabel(theElective):
    return theElective.title

class StudentEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
  
    major = StringField('Major', validators=[DataRequired()])
    gpa = StringField('GPA', validators=[DataRequired()])
    completed_courses = QuerySelectMultipleField('Completed courses:', query_factory=get_electives, get_label= getElectiveLabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    interested_fields = QuerySelectMultipleField('Interested fields: ', query_factory=get_all_fields, get_label= get_fieldlabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    known_languages = QuerySelectMultipleField('Known programming languages: ', query_factory=get_languages, get_label= getLanguageLabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    prior_research_experience = StringField('Prior Research Experience', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
            user = StudentEditForm.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('The username already exists! Please use a different username.')

    def validate_email(self, email):
            user = StudentEditForm.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('The email is already in use! Please use a different email address.')

class FacultyEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = FacultyEditForm.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username already exists! Please use a different username.')

    def validate_email(self, email):
        user = FacultyEditForm.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email is already in use! Please use a different email address.')
            

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()]) 
    general_description = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=1500)])
    time_commitment = TextAreaField('Time Commitment', validators=[DataRequired(), Length(min=1, max=50)])
    start_date = DateField('Start Date', default = date.today)
    end_date = DateField('End Date', default = date.today)
    research_fields = QuerySelectMultipleField('Field', query_factory = get_all_fields, get_label = get_fieldlabel, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    qualifications = TextAreaField('Qualifications', validators=[DataRequired(), Length(min=1, max=500)])
    faculty_name = StringField('Name', validators=[DataRequired()])
    contact_information = TextAreaField('Contact Information', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Submit')

class ApplicationForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    reference_name = StringField('Name of a reference', validators=[DataRequired()])
    reference_email = StringField('Email of a reference', validators=[DataRequired(), Email()])
    applicaton_body = TextAreaField('Describe why you chose to apply', validators=[DataRequired(), Length(min=1, max=1500)])
    submit = SubmitField('Apply')