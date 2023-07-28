import warnings
warnings.filterwarnings("ignore")
import os
basedir = os.path.abspath(os.path.dirname(__file__))

import unittest
from app import create_app, db
from app.Model.models import User, Post, Application, Field, Language, Elective
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ROOT_PATH = '..//'+basedir
    
class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='wheel', email='wheel.wilson@wsu.edu')
        u.set_password('apples')
        self.assertFalse(u.get_password('oranges'))
        self.assertTrue(u.get_password('apples'))

    def test_post(self):
        u1 = User(username='wheel', email='wheel.wilson@wsu.edu')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.get_user_posts().all(), [])
        p1 = Post(user_id=u1.id, title='Research Position Test Post', general_description='This is my test post.',
                    time_commitment='One hour', start_date='12/01/21', end_date='12/25/21', qualifications='None', faculty_name='Wheel Wilson', 
                    contact_information='wheel.wilson@wsu.edu')
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(u1.get_user_posts().count(), 1)
        self.assertEqual(u1.get_user_posts().first().title, 'Research Position Test Post')
        self.assertEqual(u1.get_user_posts().first().general_description, 'This is my test post.')
        self.assertEqual(u1.get_user_posts().first().time_commitment, 'One hour')
        self.assertEqual(u1.get_user_posts().first().start_date, '12/01/21')
        self.assertEqual(u1.get_user_posts().first().end_date, '12/25/21')
        self.assertEqual(u1.get_user_posts().first().qualifications, 'None')
        self.assertEqual(u1.get_user_posts().first().faculty_name, 'Wheel Wilson')
        self.assertEqual(u1.get_user_posts().first().contact_information, 'wheel.wilson@wsu.edu')
    
    def test_application(self):
        u2 = User(username='John', email='John@gmail.com')
        db.session.add(u2)
        a1 = Application(applicant_name = 'John', applicant_id = u2.id, reference_name = 'Bob', reference_email = 'Bob@gmail.com', application_body = 'I want to apply.')
        db.session.add(a1)
        db.session.commit()
        self.assertEqual(a1.get_user().id, u2.id)
        self.assertEqual(a1.applicant_id, u2.id)
        self.assertEqual(a1.applicant_name, 'John')
        self.assertEqual(a1.reference_email, 'Bob@gmail.com')
        self.assertEqual(a1.reference_name, 'Bob')
        self.assertEqual(a1.application_body, 'I want to apply.')


if __name__ == '__main__':
    unittest.main(verbosity=2)