from modules.seed import commit_data, clear_old_data
from app.models import Candidate, Organisation, Profession, Grade
import pytest


@pytest.mark.parametrize("model, count", [
    (Candidate, 1), (Organisation, 45), (Grade, 13), (Profession, 15)
])
def test_commit_data(model, count, test_database):
    commit_data()
    assert count == len(model.query.all())
    clear_old_data()


@pytest.mark.parametrize("model", [Candidate, Organisation, Grade, Profession])
def test_clear_old_data(model, test_database):
    clear_old_data()
    assert 0 == len(model.query.all())
    commit_data()
