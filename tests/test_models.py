from app.models import *
from datetime import date
import pytest


def test_fls_questions_create_leadership_record(test_database):
    f = FLSLeadership(
        confident_leader=5,
        inspiring_leader=4,
        when_new_role='As soon as possible',
        confidence_built=4,
        application_id=1
    )
    test_database.session.add(f)
    test_database.session.commit()
    leadership = Leadership.query.first()
    fls = FLSLeadership.query.first()
    assert leadership.id == fls.id


def test_candidate_grade_at_application_is_A():
    test_candidate = Candidate.query.first()
    current_grade = test_candidate.roles.first().grade
    assert 'Band A' == str(current_grade)


def test_candidate_cannot_apply_without_role():
    test_candidate = Candidate.query.first()
    db.session.delete(test_candidate.roles.first())  # get rid of existing role
    db.session.commit()
    with pytest.raises(AssertionError):
        Application(
                    age_range_id=1,
                    aspirational_grade=2,
                    belief_id=2,
                    working_pattern_id=1,
                    scheme_id=1,
                    application_date=date(2018, 6, 1),
                    scheme_start_date=date(2019, 9, 1),
                    per_id=1,
                    employee_number='cab10101010',
                    caring_responsibility=False,
                    long_term_health_condition=False,
                    fast_stream=False,
                    candidate_id=1,
                )
