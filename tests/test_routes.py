def test_home_status_code(test_client):
    # sends HTTP GET request to the application
    # on the specified path
    result = test_client.get('/')

    # assert the status code of the response
    assert result.status_code == 200
