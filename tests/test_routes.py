import pytest
from flask import url_for

from app.models import Grade, Organisation, Role, Profession, Location
from datetime import date
from flask_login import current_user


def test_home_status_code(test_client, logged_in_user):
    # sends HTTP GET request to the application
    # on the specified path
    result = test_client.get('/')

    # assert the status code of the response
    assert result.status_code == 200


class TestSingleUpdate:
    @pytest.mark.parametrize("update_type, form_title", [
        ("role", "Role update"),
    ])
    def test_get(self, update_type, form_title, test_client, logged_in_user):
        result = test_client.get(f'/update/single/{update_type}', follow_redirects=True)
        assert f'<h1 class="govuk-heading-xl">{form_title}</h1>' in result.data.decode('UTF-8')

    def test_post(self, test_client, test_candidate, test_database, logged_in_user):
        higher_grade = Grade.query.filter(Grade.value == 'SCS3').first()
        test_database.session.bulk_save_objects([
            Organisation(name="Number 11", department=False),
            Profession(value="Digital, Data and Technology"),
            Location(value="London")]
        )
        test_database.session.commit()
        new_org = Organisation.query.first()
        new_profession = Profession.query.first()
        new_location = Location.query.first()
        with test_client.session_transaction() as sess:
            sess['candidate-email'] = 'test.candidate@numberten.gov.uk'
        data = {
            'new-grade': higher_grade.id, 'start-date-day': '1', 'start-date-month': '1', 'start-date-year': '2019',
            'new-org': str(new_org.id), 'new-profession': str(new_profession.id),
            'new-location': str(new_location.id),
        }
        test_client.post('/update/single/role', data=data)
        saved_role = Role.query.first()
        assert saved_role.date_started == date(2019, 1, 1)
        assert saved_role.candidate_id == test_candidate.id


class TestSearchCandidate:
    def test_get(self, test_client, logged_in_user):
        result = test_client.get('/update/search-candidate')
        assert b"Most recent candidate email address" in result.data

    def test_post(self, test_client, test_candidate, logged_in_user):
        with test_client.session_transaction() as sess:
            sess['bulk-single'] = "single"
            sess['update-type'] = 'role'
        data = {'candidate-email': 'test.candidate@numberten.gov.uk'}
        result = test_client.post('/update/search-candidate', data=data, follow_redirects=True,
                                  headers={'content-type': 'application/x-www-form-urlencoded'})
        assert b'Details of the new role for test.candidate@numberten.gov.uk' in result.data

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


def test_login(logged_in_user):
    assert current_user.is_authenticated


def test_non_logged_in_users_are_redirected_to_login(test_client):
    with test_client:
        response = test_client.get('/', follow_redirects=False)
        assert response.status_code == 302  # 302 is the redirect code
        assert response.location == url_for('auth.login', _external=True)
