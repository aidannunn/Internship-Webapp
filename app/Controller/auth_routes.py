from __future__ import print_function
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for
from flask_sqlalchemy import sqlalchemy
from config import Config
from app.Model.models import  User
from app.Controller.auth_forms import StudentRegistrationForm, FacultyRegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.Controller.auth_forms import LoginForm

from app.Controller.forms import StudentEditForm, FacultyEditForm
from app import db

bp_auth = Blueprint('auth', __name__)
bp_auth.template_folder = Config.TEMPLATE_FOLDER 

@bp_auth.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    rform = StudentRegistrationForm()
    if rform.validate_on_submit():
        user = User(username=rform.username.data, email=rform.email.data,
                                    WSU_id = rform.WSU_id.data, major = rform.major.data, gpa = rform.gpa.data, 
                                    completed_courses = rform.completed_courses.data, 
                                    interested_fields = rform.interested_fields.data, 
                                    known_languages = rform.known_languages.data,
                                    prior_research_experience = rform.prior_research_experience.data, role='Student'
                                    )

        for course in rform.completed_courses.data:
            print("adding course", course.title)
            user.completed_courses.append(course)
        for field in rform.interested_fields.data:
            print("adding field:", field.name)
            user.interested_fields.append(field)
        for lang in rform.known_languages.data:
            print("adding language:", lang.name)
            user.known_languages.append(lang)

        
        user.set_password(rform.password.data)
        db.session.add(user)
        db.session.commit()
        theuser =  User.query.filter_by(id = user.id ).first()
        for c in theuser.completed_courses:
           print("register", c.title, c.id)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.index'))
    return render_template('register_student.html', form = rform)

@bp_auth.route('/register_faculty', methods=['GET', 'POST'])
def register_faculty():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    rform = FacultyRegistrationForm()
    if rform.validate_on_submit():
        user = User(username=rform.username.data, email=rform.email.data, WSU_id = rform.WSU_id.data, phone = rform.phone.data, role='Faculty')
        user.set_password(rform.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.index'))
    return render_template('register_faculty.html', form = rform)

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    lform = LoginForm()
    if lform.validate_on_submit():
        user = User.query.filter_by(username = lform.username.data).first()
        #if login fails
        if (user is None) or (user.get_password(lform.password.data) == False):
            flash('Invalid username or password')
            return redirect(url_for('routes.index'))
        login_user(user, remember = lform.remember_me.data)
        return redirect(url_for('auth.login'))
    return render_template('login.html', title='Sign In', form=lform)

@bp_auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))
