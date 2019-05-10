from app.models import *


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
