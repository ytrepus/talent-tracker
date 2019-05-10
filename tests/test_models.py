from app.models import *
import pytest
import os
from app import create_app


@pytest.fixture(scope='module', autouse=True)
def test_client():
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db'

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def test_database():
    # Create the database and the database table
    db.create_all()
    departments = [
        Organisation(
            id=1,
            name='Cabinet Office',
            department=True,
            arms_length_body=False
        ),
        Organisation(
            id=2,
            organisation_id=1,
            name='Number Ten',
            department=False,
            arms_length_body=True
        )
    ]
    grades = [Grade(value='Band A'), Grade(value='SCS3')]
    beliefs = [Belief(value='No belief'), Belief(value='Muslim')]
    schemes = [Scheme(name='FLS'), Scheme(name='SLS')]
    working_patterns = [WorkingPattern(value='Full time'), WorkingPattern(value='Part time')]
    age_ranges = [AgeRange(value='25-34'), AgeRange(value='65+')]

    yield db  # this is where the testing happens!

    db.drop_all()
    os.remove('app/test_db')


def test_fls_questions_create_leadership_record(test_database):
    f = FLSLeadership(
        confident_leader=5,
        inspiring_leader=4,
        when_new_role='As soon as possible',
        confidence_built=4
    )
    test_database.session.add(f)
    test_database.session.commit()
    leadership = Leadership.query.first()
    fls = FLSLeadership.query.first()
    assert leadership.id == fls.id
