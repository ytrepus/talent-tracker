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


# test_data = {
#             'departments': [
#                 Organisation(
#                     id=1,
#                     name='Cabinet Office',
#                     department=True,
#                     arms_length_body=False
#                 ),
#                 Organisation(
#                     id=2,
#                     name='Number Ten',
#                     parent_organisation_id=1,
#                     department=False,
#                     arms_length_body=True
#                 )
#             ],
# 'schemes': [Scheme(name='FLS'), Scheme(name='SLS')],
#             'working_patterns': [WorkingPattern(value='Full time'), WorkingPattern(value='Part time')],
#             'age_ranges': [AgeRange(value='25-34'), AgeRange(value='65+')],
#             'professions': [Profession(value='Digital Data and Technology'), Profession(value='Policy')],
#             'locations': [Location(value='London'), Location(value='Scotland')],
#
# 'test_roles': [
#                 Role(
#                     organisation_id=2,
#                     candidate_id=1,
#                     date_started=date(2018, 1, 1),
#                     profession_id=2,
#                     location_id=2,
#                     grade_id=1
#                 )
#             ],
#
#     db.session.add(
#         Application(
#             age_range_id=1,
#             aspirational_grade=2,
#             belief_id=2,
#             working_pattern_id=1,
#             scheme_id=1,
#             application_date=date(2018, 6, 1),
#             scheme_start_date=date(2019, 9, 1),
#             per_id=1,
#             employee_number='cab10101010',
#             caring_responsibility=False,
#             long_term_health_condition=False,
#             fast_stream=False,
#             candidate_id=1,
#         ),
#     )
