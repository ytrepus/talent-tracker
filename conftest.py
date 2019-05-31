import pytest
import os
import string
import random
from datetime import date
from app import create_app
from app.models import *


random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
@pytest.fixture(scope='module', autouse=True)
def test_client():
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{random_string}'

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.test_request_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module', autouse=True)
def test_database():
    # Create the database and the database table
    db.create_all()
    test_user = User(email='Test User')
    test_user.set_password("Password")
    db.session.add(test_user)
    db.session.commit()
    yield db  # this is where the testing happens!

    db.drop_all()
    os.remove(f'app/{random_string}')


@pytest.fixture()
def test_candidate(test_database):
    test_data = {
        'grades': [Grade(value='Band A', rank=2), Grade(value='SCS3', rank=1)],
        'test_candidates': [
            Candidate(
                personal_email='test.candidate@numberten.gov.uk',
                completed_fast_stream=True,
                joining_date=date(2018, 5, 1),
                joining_grade=1
            )
        ],
    }
    for key in test_data.keys():
        test_database.session.bulk_save_objects(test_data.get(key))
        test_database.session.commit()
    yield Candidate.query.first()
    Grade.query.delete()
    Candidate.query.delete()
    db.session.commit()


@pytest.fixture()
def test_grades(test_database):
    grades = [
        Grade(value='Grade 7', rank=6), Grade(value='Grade 6', rank=5), Grade(value='Deputy Director (SCS1)', rank=4),
        Grade(value='Admin Assistant (AA)', rank=7)
    ]
    test_database.session.add_all(grades)
    test_database.session.commit()
    yield

    Grade.query.delete()
    db.session.commit()


@pytest.fixture
def logged_in_user(test_client, test_database):
    with test_client:
        test_client.post('/auth/login', data={'email-address': "Test User", 'password': 'Password'})
        yield
