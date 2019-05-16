import csv
import os

from app.models import FLSLeadership, SLSLeadership


def test_home_status_code(test_client):
    # sends HTTP GET request to the application
    # on the specified path
    result = test_client.get('/')

    # assert the status code of the response
    assert result.status_code == 200


def test_bulk_update(test_client):
    test_data = {
            "id": 1,
            "application_id": 1,
            "confident_leader": 4,
            "inspiring_leader": 3,
            "when_new_role": "Next 6 months",
            "type": "fls_leadership",
            "increased_visibility": 4
    }
    with open('tests/test_fls_leadership_data.csv', mode='w') as csv_file:
        fieldnames = list(test_data.keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(test_data)
    with open('tests/test_fls_leadership_data.csv', 'rb') as test_file:
        data = {"update_type": "FLS", "file": (test_file, 'test_file.csv')}
        request = test_client.post('/update/bulk', data=data, follow_redirects=True, content_type='multipart/form-data')
    os.remove(os.path.join(f"tests/test_fls_leadership_data.csv"))
    os.remove(os.path.join(f"app/uploads/test_file.csv"))
    leadership_questions = FLSLeadership.query.get(1)
    sls_questions = SLSLeadership.query.get(1)
    assert request.status_code == 200
    assert leadership_questions is not None
    assert sls_questions is None  # shouldn't make an SLSLeadership row
