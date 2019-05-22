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


def test_candidate_grade_at_application_is_A(test_candidate):
    candidate = Candidate.query.first()
    db.session.add(Role(grade_id=1, candidate_id=candidate.id))
    db.session.commit()
    current_grade = candidate.roles.first().grade
    assert 'Band A' == current_grade.value


def test_candidate_cannot_apply_without_role(test_candidate):
    with pytest.raises(AssertionError):
        Application(
                    aspirational_grade=2,
                    scheme_id=1,
                    application_date=date(2018, 6, 1),
                    scheme_start_date=date(2019, 9, 1),
                    per_id=1,
                    employee_number='cab10101010',
                    candidate_id=1,
                )
