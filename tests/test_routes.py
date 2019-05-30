import pytest


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
            result = test_client.post('/update/search-candidate', json=data, follow_redirects=True)
        assert b'Details of the new role for test.candidate@numberten.gov.uk' in result.data
