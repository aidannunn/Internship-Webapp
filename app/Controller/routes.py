from __future__ import print_function
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from config import Config

from app import db
from app.Model.models import postFields, Field, Post, Application, User
from app.Controller.forms import PostForm, StudentEditForm, FacultyEditForm, ApplicationForm
from sqlalchemy import desc

bp_routes = Blueprint('routes', __name__)
bp_routes.template_folder = Config.TEMPLATE_FOLDER #'..\\View\\templates'




@bp_routes.route('/', methods=['GET', 'POST'])
@bp_routes.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #for each field in the post, if that field is in the user's interests, include it in the recommended posts
    recommended_posts = []
    other_posts = []
    all_posts = Post.query.order_by(Post.title).all()
    user = current_user

    if current_user.is_anonymous or current_user.role == 'Faculty':
        return render_template('index.html', title="Research Positions", posts=all_posts, user = current_user)
    else:
        all_unapplied_posts = user.get_unapplied_posts()
        for post in all_unapplied_posts:
            for field in post.fields:
                if field in current_user.interested_fields and post not in recommended_posts:
                    recommended_posts.append(post)
        for post in all_unapplied_posts:
            for field in post.fields:
                if field not in current_user.interested_fields and post not in other_posts and post not in recommended_posts:
                    other_posts.append(post)
    
    return render_template('index.html', title="Research Positions", posts = all_posts, recommended_posts = recommended_posts, other_posts = other_posts, user = current_user)

@bp_routes.route('/post_position', methods=['GET', 'POST'])
@login_required
def post_position():
    pform = PostForm()
    if pform.validate_on_submit():
        newPost = Post(title=pform.title.data, general_description = pform.general_description.data,
                                                user_id = current_user.id, 
                                                time_commitment = pform.time_commitment.data,
                                                start_date = pform.start_date.data,
                                                end_date = pform.end_date.data,
                                                qualifications = pform.qualifications.data,
                                                faculty_name = pform.faculty_name.data,
                                                contact_information = pform.contact_information.data
                                                )
        for field in pform.research_fields.data:
            newPost.fields.append(field)
        db.session.add(newPost)
        db.session.commit()
        flash("Research position successfully posted")
        return redirect(url_for('routes.index'))
    return render_template('create_position.html', form = pform)

@bp_routes.route('/delete/<post_id>', methods=['DELETE', 'POST'])
@login_required
def delete(post_id):
    thepost = Post.query.filter_by(id = post_id).first()
    applications = Application.query.filter_by(post_id = thepost.id)
    for app in applications:
        app.application_status = "Position is currently unavailable"
    if thepost:
        for t in thepost.fields:
            thepost.fields.remove(t)
        db.session.commit()
    db.session.delete(thepost)
    db.session.commit()
    flash("Post deleted successfuly")
    return redirect(url_for('routes.index'))

@bp_routes.route('/post_application/<post_id>', methods=['GET', 'POST'])
@login_required
def post_application(post_id):
    thepost = Post.query.filter_by(id = post_id).first()
    if thepost:
        aform = ApplicationForm()
        if aform.validate_on_submit():
            user_id = current_user.id
            theuser = User.query.filter_by(id = user_id).first()
            newApplication = Application(applicant_id = user_id, applicant_name = aform.name.data,  reference_name = aform.reference_name.data, 
                                         reference_email = aform.reference_email.data, application_body = aform.applicaton_body.data,
                                         application_status = "Pending..." ,post_id = post_id)
            db.session.add(newApplication)
            db.session.commit()
            flash("Application sent!")
            return redirect(url_for('routes.index'))
    return render_template('post_application.html', form=aform)

@bp_routes.route('/accept_application/<application_id>', methods=['GET', 'POST'])
@login_required
def accept_application(application_id):
    application = Application.query.filter_by(id = application_id).first()
    application.application_status = "Accepted!!!"
    db.session.commit()
    flash("Application Accepted!")
    return redirect(url_for('routes.index'))

@bp_routes.route('/reject_application/<application_id>', methods=['GET', 'POST'])
@login_required
def reject_application(application_id):
    application = Application.query.filter_by(id = application_id).first()
    application.application_status = "Rejected :("
    db.session.commit()
    flash("Application Rejected!")
    return redirect(url_for('routes.index'))

@bp_routes.route('/remove_application/<application_id>', methods=['GET', 'POST'])
@login_required
def remove_application(application_id):
    form = Application.query.filter_by(id = application_id).first()
    db.session.commit()
    db.session.delete(form)
    db.session.commit()
    flash("Application Successfully withdrawn!")
    return redirect(url_for('routes.index'))

@bp_routes.route('/view_applications/<current_user_id>', methods=['GET', 'POST'])
@login_required
def view_applications(current_user_id):
    if (current_user.role == 'Student'):
        applications = Application.query.filter_by(applicant_id = current_user_id).all()
    elif (current_user.role == 'Faculty'):
        applications = Application.query.join(Application.post).filter_by(user_id = current_user_id).all()
    return render_template('view_applications.html', applications = applications)


@bp_routes.route('/edit_student_profile', methods = ['GET', 'POST'])
@login_required
def edit_student_profile():
    eform = StudentEditForm()
    if request.method == 'POST':
        current_user.username = eform.username.data
        current_user.email = eform.email.data
        current_user.major = eform.major.data
        current_user.gpa = eform.gpa.data
        
        #user = User.query.filter_by(id = current_user.id).first() -- This line and the one below that is commented out is not needed 
        #user.completed_courses.clear()
        for course in current_user.completed_courses:
            current_user.completed_courses.remove(course)
        

        for course in eform.completed_courses.data:
            print("adding course", course.title)
            current_user.completed_courses.append(course)
        db.session.add(current_user)
        db.session.commit()

        for field in current_user.interested_fields:
            current_user.interested_fields.remove(field)
        
        for field in eform.interested_fields.data:
            print("adding field", field.name)
            current_user.interested_fields.append(field)
        db.session.add(current_user)
        db.session.commit() 
        
        for lang in current_user.known_languages: 
             current_user.known_languages.remove(lang)

        for lang in eform.known_languages.data: 
            print("adding lang:", lang.name)
            current_user.known_languages.append(lang)
        db.session.add(current_user)
        db.session.commit()


        current_user.prior_research_experience = eform.prior_research_experience.data
        db.session.add(current_user)
        db.session.commit()

        flash("Your changes have been saved")
        return redirect(url_for('routes.display_StudentProfile'))
    
    elif request.method == 'GET':
        eform.username.data = current_user.username
        eform.email.data = current_user.email
        eform.major.data = current_user.major 
        eform.gpa.data = current_user.gpa
        eform.completed_courses.data = current_user.get_electives()
        eform.interested_fields.data = current_user.get_fields()
        eform.known_languages.data = current_user.get_languages()
        eform.prior_research_experience.data = current_user.prior_research_experience
    else:
        pass

    return render_template('edit_student_profile.html', title ='Edit Profile', form = eform)


@bp_routes.route('/edit_faculty_profile', methods = ['GET', 'POST'])
@login_required
def edit_faculty_profile():
    eform = FacultyEditForm()
    if request.method == 'POST':
        current_user.username = eform.username.data
        current_user.email = eform.email.data
        current_user.phone = eform.phone.data
        db.session.add(current_user)
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for('routes.display_FacultyProfile'))
    elif request.method == 'GET':
        eform.username.data = current_user.username
        eform.email.data = current_user.email
        eform.phone.data = current_user.phone 
    else:
        pass

    return render_template('edit_faculty_profile.html', title ='Edit Profile', form = eform)


    

@bp_routes.route('/display_StudentProfile', methods = ['GET'])
@login_required
def display_StudentProfile():
    #user = User.query.filter_by(id = current_user.id).all()
    return render_template('display_StudentProfile.html', title ='Displaying Student Profile...', user = current_user)
@bp_routes.route('/display_Profile/<application_id>', methods = ['GET', 'POST'])
@login_required
def show_StudentProfile(application_id):
    theapp = Application.query.filter_by(id = application_id).first()
    user = theapp.get_user()
    return render_template('display_StudentProfile.html', title ='Displaying Student Profile...', user = user)

@bp_routes.route('/display_FacultyProfile', methods = ['GET'])
@login_required
def display_FacultyProfile():
    return render_template('display_FacultyProfile.html', title ='Displaying Faculty Profile...', user = current_user)
