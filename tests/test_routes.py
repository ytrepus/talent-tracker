import pytest
from app.models import Grade, Organisation, Role, Profession, Location
from datetime import date

def test_home_status_code(test_client):
    # sends HTTP GET request to the application
    # on the specified path
    result = test_client.get('/')

    # assert the status code of the response
    assert result.status_code == 200


class TestSingleUpdate:
    @pytest.mark.parametrize("update_type, form_title", [
        ("role", "Role update"),
    ])
    def test_get(self, update_type, form_title, test_client):
        result = test_client.get(f'/update/single/{update_type}')
        assert f'<h1 class="govuk-heading-xl">{form_title}</h1>' in result.data.decode('UTF-8')

    def test_post(self, test_client, test_candidate, test_database):
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
        with test_client:
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
    def test_get(self, test_client):
        result = test_client.get('/update/search-candidate')
        assert b"Most recent candidate email address" in result.data

    def test_post(self, test_client, test_candidate):
        with test_client:
            with test_client.session_transaction() as sess:
                sess['bulk-single'] = "single"
                sess['update-type'] = 'role'
            data = {'candidate-email': 'test.candidate@numberten.gov.uk'}
            result = test_client.post('/update/search-candidate', data=data, follow_redirects=True,
                                      headers={'content-type': 'application/x-www-form-urlencoded'})
            assert b'Details of the new role for test.candidate@numberten.gov.uk' in result.data
