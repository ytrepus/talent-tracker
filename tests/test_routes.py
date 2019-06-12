import pytest
from flask import url_for, session

from app.models import Grade, Organisation, Profession, Location, Role
from flask_login import current_user


def test_home_status_code(test_client, logged_in_user):
    # sends HTTP GET request to the application
    # on the specified path
    result = test_client.get('/')

    # assert the status code of the response
    assert result.status_code == 200


class TestNewEmail:
    def test_get(self, test_client, logged_in_user):
        result = test_client.get('/update/email-address')
        assert b"Has the candidate got a new email address?" in result.data

    def test_post(self, test_client, logged_in_user, test_candidate):

        with test_client.session_transaction() as sess:
            sess['candidate-id'] = 1
        data = {"update-email-address": "true", "new-email-address": "new-test-email@gov.uk"}
        test_client.post('/update/email-address', data=data)
        assert "new-test-email@gov.uk" == session.get("new-email")


class TestSingleUpdate:
    @pytest.mark.parametrize("update_type, form_title", [
        ("role", "Role update"),
    ])
    def test_get(self, update_type, form_title, test_client, test_candidate, logged_in_user, test_roles):
        with test_client.session_transaction() as sess:
            sess['candidate-id'] = 1
        result = test_client.get(f'/update/single/{update_type}', follow_redirects=False)
        print(session)
        print(result.data)
        assert f'<h1 class="govuk-heading-xl">{form_title}</h1>' in result.data.decode('UTF-8')

    def test_post(self, test_client, test_candidate, test_session, logged_in_user):
        higher_grade = Grade.query.filter(Grade.value == 'SCS3').first()
        test_session.bulk_save_objects([
            Organisation(name="Number 11", department=False),
            Profession(value="Digital, Data and Technology"),
            Location(value="London")]
        )
        test_session.commit()
        new_org = Organisation.query.first()
        new_profession = Profession.query.first()
        new_location = Location.query.first()
        data = {
            'new-grade': higher_grade.id, 'start-date-day': '1', 'start-date-month': '1', 'start-date-year': '2019',
            'new-org': str(new_org.id), 'new-profession': str(new_profession.id),
            'new-location': str(new_location.id), 'temporary-promotion': '1'
        }
        test_client.post('/update/single/role', data=data)
        assert data.keys() == session.get('new-role').keys()


class TestSearchCandidate:
    def test_get(self, test_client, logged_in_user):
        result = test_client.get('/update/search-candidate')
        assert b"Most recent candidate email address" in result.data

    def test_post(self, test_client, test_candidate, logged_in_user, test_roles):
        with test_client.session_transaction() as sess:
            sess['bulk-single'] = "single"
            sess['update-type'] = 'role'
        data = {'candidate-email': 'test.candidate@numberten.gov.uk'}
        result = test_client.post('/update/search-candidate', data=data, follow_redirects=True,
                                  headers={'content-type': 'application/x-www-form-urlencoded'})
        assert b'Details of the new role for test.candidate@numberten.gov.uk' in result.data

        assert 1 == session.get('candidate-id')

    def test_given_candidate_email_doesnt_exist_when_user_searches_then_user_is_redirected_to_new_search(self,
                                                                                                         test_client,
                                                                                                         logged_in_user):
        with test_client.session_transaction() as sess:
            sess['bulk-single'] = "single"
            sess['update-type'] = 'role'
        data = {'candidate-email': 'no-such-candidate@numberten.gov.uk'}
        result = test_client.post('/update/search-candidate', data=data, follow_redirects=False,
                                  headers={'content-type': 'application/x-www-form-urlencoded'})
        assert result.status_code == 302
        assert result.location == f"http://localhost{url_for('route_blueprint.search_candidate')}"


def test_check_details(logged_in_user, test_client, test_session, test_candidate, test_grades, test_locations,
                       test_orgs, test_professions):
    higher_grade = Grade.query.filter(Grade.value == 'SCS3').first()
    new_org = Organisation.query.first()
    new_profession = Profession.query.first()
    new_location = Location.query.first()
    with test_client.session_transaction() as sess:
        sess['new-role'] = {
            'new-grade': higher_grade.id, 'start-date-day': 1, 'start-date-month': 1, 'start-date-year': 2019,
            'new-org': new_org.id, 'new-profession': new_profession.id,
            'new-location': new_location.id, 'temporary-promotion': 1
        }
        sess['human-readable-new-role'] = dict()
        sess['candidate-id'] = test_candidate.id
    test_client.post('/update/check-your-answers')
    latest_role = test_candidate.roles.order_by(Role.id.desc()).first()
    assert "Organisation 1" == Organisation.query.get(latest_role.organisation_id).name


def test_login(logged_in_user):
    assert current_user.is_authenticated


def test_non_logged_in_users_are_redirected_to_login(test_client):
    with test_client:
        response = test_client.get('/', follow_redirects=False)
        assert response.status_code == 302  # 302 is the redirect code
        assert response.location == url_for('auth.login', _external=True)
