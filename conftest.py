import pytest
from datetime import date
from app import create_app
from app.models import db as _db
from config import TestConfig
from app.models import *


@pytest.fixture(scope='session', autouse=True)
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


@pytest.fixture(scope='session')
def db(test_client):
    _db.app = test_client
    _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def test_session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    test_user = User(email='Test User')
    test_user.set_password("Password")
    db.session.add(test_user)
    db.session.add_all([Scheme(id=1, name='FLS'), Scheme(id=2, name='SLS')])
    db.session.commit()

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.fixture
def test_candidate(test_session):
    candidate = Candidate(
                email_address='test.candidate@numberten.gov.uk',
                completed_fast_stream=True,
                joining_date=date(2010, 5, 1),
                joining_grade=1,
            )
    candidate.roles.append(Role(date_started=date(2010, 5, 1), temporary_promotion=False))
    test_data = {
        'grades': [Grade(value='Band A', rank=2), Grade(value='SCS3', rank=1)],
        'test_candidates': [candidate],
    }
    for key in test_data.keys():
        test_session.add_all(test_data.get(key))
        test_session.commit()
    yield Candidate.query.first()


@pytest.fixture
def test_candidate_applied_to_fls(test_candidate, test_session):
    print(test_candidate.roles.all())
    test_candidate.applications.append(Application(application_date=date(2019, 6, 1), scheme_id=1))
    test_session.add(test_candidate)
    test_session.commit()
    yield Candidate.query.first()


@pytest.fixture
def test_candidate_applied_and_promoted(test_candidate_applied_to_fls, test_session):
    test_candidate_applied_to_fls.roles.append(Role(date_started=date(2020, 1, 1), temporary_promotion=False))
    test_session.add(test_candidate_applied_to_fls)
    test_session.commit()
    yield


@pytest.fixture
def test_roles(test_session, test_candidate):
    roles = [Role(date_started=date(2019, 1, 1), candidate_id=test_candidate.id,
                  grade_id=Grade.query.filter(Grade.value == 'Band A').first().id)]
    test_session.add_all(roles)
    test_session.commit()
    yield


@pytest.fixture
def test_grades(test_session):
    grades = [
        Grade(value='Grade 7', rank=6), Grade(value='Grade 6', rank=5),
        Grade(value='Deputy Director (SCS1)', rank=4), Grade(value='Admin Assistant (AA)', rank=7)
    ]
    test_session.add_all(grades)
    test_session.commit()
    yield


@pytest.fixture
def test_locations(test_session):
    locations = [Location(value='The North'), Location(value="The South")]
    test_session.add_all(locations)
    test_session.commit()
    yield


@pytest.fixture
def test_orgs(test_session):
    test_session.add_all([Organisation(name="Organisation 1"), Organisation(name="Organisation 2")])
    test_session.commit()
    yield


@pytest.fixture
def test_professions(test_session):
    test_session.add_all([Profession(value="Profession 1"), Profession(value="Profession 2")])
    test_session.commit()
    yield


@pytest.fixture
def test_ethnicities(test_session):
    test_session.add_all([Ethnicity(value="White British"), Ethnicity(value="Black British", bame=True)])
    test_session.commit()
    yield


@pytest.fixture
def test_multiple_candidates_multiple_ethnicities(test_session, test_ethnicities):
    test_session.add_all([Candidate(ethnicity_id=Ethnicity.query.filter_by(value="Black British").first().id) for i in range(10)])
    test_session.add_all([Candidate(ethnicity_id=Ethnicity.query.filter_by(value="White British").first().id) for i in range(10)])
    test_session.commit()
    yield


@pytest.fixture
def test_promoted_candidates(test_session, test_multiple_candidates_multiple_ethnicities):
    bb_candidates = Candidate.query.filter_by(ethnicity_id=Ethnicity.query.filter_by(value="Black British").first().id).all()
    wb_candidates = Candidate.query.filter_by(ethnicity_id=Ethnicity.query.filter_by(value="White British").first().id).all()
    test_session.add_all(
        [candidate.roles.extend(
            [Role(date_started=date(2019, 1, 1)), Role(date_started=date(2020, 1, 1))])
            for candidate in bb_candidates[0:7]]
    )
    test_session.add_all(
        [candidate.roles.extend(
            [Role(date_started=date(2019, 1, 1)), Role(date_started=date(2020, 1, 1))])
            for candidate in wb_candidates[0:5]]
    )
    test_session.commit()
    yield


@pytest.fixture
def test_applications(test_session, test_promoted_candidates):
    test_session.add_all(
        [
            candidate.applications.append(Application(application_date=date(2019, 6, 1)))
            for candidate in Candidate.query.all()
        ]
    )

@pytest.fixture
def logged_in_user(test_client):
    with test_client:
        test_client.post('/auth/login', data={'email-address': "Test User", 'password': 'Password'})
        yield
        test_client.get('/auth/logout')
