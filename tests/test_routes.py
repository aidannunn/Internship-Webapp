"""
This file contains the functional tests for the routes.
These tests use GETs and POSTs to different URLs to check for the proper behavior.
Resources:
    https://flask.palletsprojects.com/en/1.1.x/testing/ 
    https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/ 
"""
import os
import pytest
from app import create_app, db
from app.Model.models import User, Post, Field, Language, Elective
from config import Config


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True



@pytest.fixture(scope='module')
def test_client():
    # create the flask application ; configure the app for tests
    flask_app = create_app(config_class=TestConfig)

    db.init_app(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()
 
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
 
    yield  testing_client 
    # this is where the testing happens!
 
    ctx.pop()

def new_user(uname, uemail,passwd):
    user = User(username=uname, email=uemail)
    user.set_password(passwd)
    return user


def init_tags():
    # initialize the tags
    if Field.query.count() == 0:
        fields = ['Computer Science','Biology', 'Physics', 'Psychology']
        for t in fields:
            db.session.add(Field(name=t))
        db.session.commit()
        print(fields)

    if Language.query.count() == 0:
        langs = ['C++', 'Scratch', 'Python', 'HTML', 'Haskell']
        for t in langs:
            db.session.add(Language(name=t))
        db.session.commit()
        print(langs)

    if Elective.query.count() == 0:
        electives = ['Machine Learning', 'Big Data', 'Introduction to Killer AI', 'OOP', 'Finite Automata', 'Programming Language Design']
        for t in electives:
            db.session.add(Elective(title=t))
        db.session.commit()
        print(electives)
    
    return None

@pytest.fixture
def init_database():
    # Create the database and the database table
    db.create_all()
    # initialize the tags
    init_tags()
    #add a user    
    user1 = new_user(uname='aidan', uemail='aidan.nunn@wsu.edu',passwd='123')
    # Insert user data
    db.session.add(user1)
    # Commit the changes for the users
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()

def test_register_faculty_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register_faculty' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/register_faculty')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_register_student_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register_student' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/register_student')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_register_faculty(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register_faculty' form is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.post('/register_faculty', 
                          data=dict(username='wheel', email='wheel.wilson@wsu.edu', WSU_id = '12345678', 
                          phone='425-123-2345', password="bad-bad-password", password2="bad-bad-password"),
                          follow_redirects = True)
    assert response.status_code == 200

    s = db.session.query(User).filter(User.username=='wheel')
    assert s.first().email == 'wheel.wilson@wsu.edu'
    assert s.first().WSU_id == '12345678'
    assert s.first().phone == '425-123-2345'
    assert s.count() == 1
    assert b"Sign In" in response.data   
    assert b"Please log in to access this page." in response.data

def test_register_student(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register_student' form is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    """

    courses_tags = list( map(lambda t: t.id, Elective.query.all()[:3]))
    field_tags = list( map(lambda t: t.id, Field.query.all()[:2]))
    lang_tags = list( map(lambda t: t.id, Language.query.all()[:1]))

    # Create a test client using the Flask application configured for testing
    response = test_client.post('/register_student', 
                          data=dict(username='timmy', email='timmy.turnpike@wsu.edu', WSU_id = '098576354', 
                          major='Computer Science', gpa='3.3', prior_research_experience='None', 
                          completed_courses=courses_tags, interested_fields=field_tags,  known_languages=lang_tags,
                          password="bad-bad-password", password2="bad-bad-password"),
                          follow_redirects = True)
    assert response.status_code == 200

    s = db.session.query(User).filter(User.username=='timmy')
    assert s.first().email == 'timmy.turnpike@wsu.edu'
    assert s.first().WSU_id == '098576354'
    assert s.first().major == 'Computer Science'
    assert s.first().gpa == '3.3'
    assert s.first().get_electives().count() == 3
    assert s.first().get_fields().count() == 2
    assert s.first().get_languages().count() == 1
    assert s.first().prior_research_experience == 'None'
    assert s.count() == 1
    assert b"Sign In" in response.data   
    assert b"Please log in to access this page." in response.data

def test_invalidlogin(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with wrong credentials
    THEN check that the response is valid and login is refused 
    """
    response = test_client.post('/login', 
                          data=dict(username='aidan', password='12345',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_login_logout(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct credentials
    THEN check that the response is valid and login is succesfull 
    """
    response = test_client.post('/login', 
                          data=dict(username='aidan', password='123',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200

    response = test_client.get('/logout',                       
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Please log in to access this page." in response.data

def test_postResearchPosition(test_client,init_database):
    """
    GIVEN a Flask application configured for testing , after user logs in,
    WHEN the '/post_position' page is requested (GET)  AND /PostForm' form is submitted (POST)
    THEN check that response is valid and the class is successfully created in the database
    """
    #login
    response = test_client.post('/login', 
                        data=dict(username='aidan', password='123',remember_me=False),
                        follow_redirects = True)
    assert response.status_code == 200
    
    #test the form for posting a research position
    response = test_client.get('/post_position')
    assert response.status_code == 200
    
    #test posting a research position
    tags1 = list( map(lambda t: t.id, Field.query.all()[:3]))  # should only pass 'id's of the tags. See https://stackoverflow.com/questions/62157168/how-to-send-queryselectfield-form-data-to-a-flask-view-in-a-unittest
    print("TESTING********************: ", tags1)
    response = test_client.post('/post_position', 
                          data=dict(title='My test post', general_description='This is my first test post.', 
                          time_commitment='1 hour', qualifications='None', faculty_name='Wheel Wilson', 
                          contact_information='Wheel_Wilson@gmail.com', research_fields = tags1),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"My test post" in response.data 

    c = db.session.query(Post).filter(Post.title =='My test post')
    assert c.first().get_fields().count() == 3 #should have 3 tags
    assert c.count() >= 1 #There should be at least one post with title "My test post"


    tags2 = list( map(lambda t: t.id, Field.query.all()[1:3]))  # should only pass 'id's of the tags. See https://stackoverflow.com/questions/62157168/how-to-send-queryselectfield-form-data-to-a-flask-view-in-a-unittest
    print("TESTING********************: ", tags2)
    response = test_client.post('/post_position', 
                          data=dict(title='Second test post', general_description='Here is another post.', time_commitment='1 hour', qualifications='None', faculty_name='Wheel Wilson', contact_information='Wheel_Wilson@gmail.com', research_fields = tags2),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Second test post" in response.data 
    assert b"Here is another post." in response.data 

    c = db.session.query(Post).filter(Post.general_description =='Here is another post.')
    assert c.first().get_fields().count() == 2  # Should have 2 tags
    assert c.count() >= 1 #There should be at least one post with body "Here is another post."

    assert db.session.query(Post).count() == 2

    #finally logout
    response = test_client.get('/logout',                       
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Please log in to access this page." in response.data