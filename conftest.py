import pytest
import os
from datetime import date
from app import create_app
from app.models import *
from config import TestConfig


@pytest.fixture(scope='module', autouse=True)
def test_client():
    flask_app = create_app(TestConfig)

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
    os.remove('app/testing-database')


@pytest.fixture(scope="class")
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


@pytest.fixture(scope="class")
def test_roles(test_database, test_candidate):
    roles = [Role(date_started=date(2019, 1, 1), candidate_id=test_candidate.id,
                  grade_id=Grade.query.filter(Grade.value == 'Band A').first().id)]
    test_database.session.add_all(roles)
    test_database.session.commit()
    yield
    Role.query.delete()
    db.session.commit()


@pytest.fixture(scope="class")
def test_grades(test_database):
    grades = [
        Grade(value='Grade 7', rank=6), Grade(value='Grade 6', rank=5),
        Grade(value='Deputy Director (SCS1)', rank=4), Grade(value='Admin Assistant (AA)', rank=7)
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
        test_client.get('/auth/logout')
