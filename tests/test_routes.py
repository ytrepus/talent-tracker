import pytest


def test_home_status_code(test_client):
    # sends HTTP GET request to the application
    # on the specified path
    result = test_client.get('/')

    # assert the status code of the response
    assert result.status_code == 200


class TestSingleUpdate:
    @pytest.mark.parametrize("update_type, form_title", [
        ("role", "Role update"), ("fls-survey", "FLS Survey update"), ("sls-survey", "SLS Survey update")
    ])
    def test_get(self, update_type, form_title, test_client):
        result = test_client.get(f'/update/single/{update_type}')
        assert f'<h1 class="govuk-heading-xl">{form_title}</h1>' in result.data.decode('UTF-8')
