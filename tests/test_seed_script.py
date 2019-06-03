from modules.seed import commit_data, clear_old_data
from app.models import Candidate, Organisation, Profession, Grade


def test_commit_data(test_database):
    commit_data()
    assert len(Candidate.query.all()) == 1
    assert len(Organisation.query.all()) == 45
    assert len(Grade.query.all()) == 11
    assert len(Profession.query.all()) == 15


def test_clear_old_data(test_database):
    clear_old_data()
    assert len(Candidate.query.all()) == 0
    assert len(Organisation.query.all()) == 0
    assert len(Grade.query.all()) == 0
    assert len(Profession.query.all()) == 0
