from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


postFields = db.Table('post_fields',
                db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                db.Column('field_id', db.Integer, db.ForeignKey('field.id'))
                )

userLanguages = db.Table('user_languages',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('language_id', db.Integer, db.ForeignKey('language.id'))
                )

userElectives = db.Table('user_electives',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('elective_id', db.Integer, db.ForeignKey('elective.id'))
                )

userInterests = db.Table('user_interests',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('field_id', db.Integer, db.ForeignKey('field.id'))
                )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    WSU_id = db.Column(db.String(10), unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))
    major = db.Column(db.String(20))
    gpa = db.Column(db.String(4))
    completed_courses = db.relationship('Elective', secondary = userElectives, 
                                  primaryjoin=(userElectives.c.user_id == id), 
                                  backref=db.backref('userElectives', 
                                  lazy='dynamic'), lazy='dynamic')
    interested_fields = db.relationship('Field', secondary = userInterests, 
                                  primaryjoin=(userInterests.c.user_id == id), 
                                  backref=db.backref('userInterests', 
                                  lazy='dynamic'), lazy='dynamic')
    known_languages = db.relationship('Language', secondary = userLanguages, 
                                  primaryjoin=(userLanguages.c.user_id == id), 
                                  backref=db.backref('userLanguages', 
                                  lazy='dynamic'), lazy='dynamic')
    prior_research_experience = db.Column(db.String(200))
    phone = db.Column(db.String(12), unique=True)
    posts = db.relationship('Post', backref='writer', lazy='dynamic')
    
    def __repr__(self):
        return '{}'.format(self.username)

    def get_unapplied_posts(self):
        posts = Post.query.all()
        
        #applications = Application.query.filter_by(applicant_id = self.id).all()
        unapplied = []
        for post in posts:
            checker = 0
            for app in post.applications:
                if app.applicant_id == self.id:
                    checker = 1
            if checker != 1:
                unapplied.append(post)
            
        return unapplied

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_user_posts(self):
        return self.posts
    
    def get_electives(self):
        return self.completed_courses

    def get_languages(self):
        return self.known_languages

    def get_fields(self):
        return self.interested_fields


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    def __repr__(self):
        return ' {} '.format(self.name)

class Elective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    def __repr__(self):
        return ' {} '.format(self.title)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'))
    title = db.Column(db.String(150))
    general_description = db.Column(db.String(1500))
    time_commitment = db.Column(db.String(50))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    fields = db.relationship('Field', secondary = postFields, 
                                  primaryjoin=(postFields.c.post_id == id), 
                                  backref=db.backref('postFields', 
                                  lazy='dynamic'), lazy='dynamic')
    qualifications = db.Column(db.String(500))
    faculty_name = db.Column(db.String(50))
    contact_information = db.Column(db.String(100))
    applications = db.relationship('Application', backref='post', lazy='dynamic')
    
    def get_fields(self):
        return self.fields
    def get_applications(self):
        return self.applications



class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    def __repr__(self):
        return ' {} '.format(self.name)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    applicant_name = db.Column(db.String(50))
    applicant_id = db.Column(db.Integer)
    reference_name = db.Column(db.String(50))
    reference_email = db.Column(db.String(50))
    application_body = db.Column(db.String(1500))
    application_status = db.Column(db.String(15))

    def get_user(self):
        return User.query.filter_by(id=self.applicant_id).first()
    
