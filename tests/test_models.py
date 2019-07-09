from app.models import FLSLeadership, Leadership, Candidate, Role, Grade, Application, Promotion
from datetime import date
import pytest


def test_fls_questions_create_leadership_record(test_session):
    f = FLSLeadership(
        confident_leader=5,
        inspiring_leader=4,
        when_new_role='As soon as possible',
        confidence_built=4,
        application_id=1
    )
    test_session.add(f)
    test_session.commit()
    leadership = Leadership.query.first()
    fls = FLSLeadership.query.first()
    assert leadership.id == fls.id


class TestCandidate:
    def test_current_grade_returns_correct_grade(self, test_candidate, test_session):
        grades = Grade.query.order_by(Grade.rank.asc()).all()
        roles = [Role(date_started=date(2017 + i, 1, 1), grade=grades[i]) for i in range(3)]
        test_candidate.roles.extend(roles)
        test_session.add(test_candidate)
        test_session.commit()
        assert Candidate.query.get(test_candidate.id).current_grade().value == 'Deputy Director (SCS1)'

    @pytest.mark.parametrize(
        "list_of_role_data, expected_outcome",
        [
            (  # substantive promotion after the date
                [
                    {'date-started': date(2019, 1, 1), 'grade-value': "Grade 7"},
                    {'date-started': date(2019, 12, 1), 'grade-value': "Grade 6", 'temporary': False}
                ],
                True

            ),
            (  # temporary promotion after the date
                [
                    {'date-started': date(2019, 1, 1), 'grade-value': "Grade 7"},
                    {'date-started': date(2019, 12, 1), 'grade-value': "Grade 6", 'temporary': True}
                ],
                False

            ),
            (  # level transfer after the date
                [
                    {'date-started': date(2019, 1, 1), 'grade-value': "Grade 7"},
                    {'date-started': date(2019, 12, 1), 'grade-value': "Grade 7"}
                ],
                False

            ),
            (  # a promotion that hasn't happened yet
                [
                    {'date-started': date(2019, 1, 1), 'grade-value': "Grade 7"},
                    {'date-started': date(2020, 3, 1), 'grade-value': "Grade 6", 'temporary': False}
                ],
                False

            ),
            (  # level transfer that hasn't happened yet
                [
                    {'date-started': date(2019, 1, 1), 'grade-value': "Grade 7"},
                    {'date-started': date(2020, 3, 1), 'grade-value': "Grade 7"}
                ],
                False

            ),
        ]
    )
    def test_promoted_when_started(self, list_of_role_data, expected_outcome, test_candidate, test_session):
        if list_of_role_data[1].get('temporary'):
            role_change = Promotion.query.filter_by(value="temporary").first()
        else:
            role_change = Promotion.query.filter_by(value="substantive").first()
        test_candidate: Candidate
        test_candidate.roles.extend([
            Role(date_started=list_of_role_data[0].get('date-started'),
                 grade=Grade.query.filter_by(value=list_of_role_data[0].get('grade-value')).first(),
                 temporary_promotion=False),
            Role(date_started=list_of_role_data[1].get('date-started'),
                 grade=Grade.query.filter_by(value=list_of_role_data[1].get('grade-value')).first(),
                 temporary_promotion=list_of_role_data[1].get('temporary'), role_change=role_change)
        ])
        assert test_candidate.promoted('2019-09-01', date(2020, 1, 1)) is expected_outcome

    def test_current_scheme_returns_current_scheme(self, test_candidate_applied_to_fls):
        assert test_candidate_applied_to_fls.current_scheme().name == 'FLS'

    @pytest.mark.parametrize("prior_application, expected_output", [
        (Application(application_date=date(2018, 6, 1)), date(2019, 6, 1)),
        (Application(application_date=date(2020, 6, 1)), date(2020, 6, 1))
    ])
    def test_current_application_returns_correct_application(self, prior_application, expected_output,
                                                             test_candidate_applied_to_fls):
        test_candidate_applied_to_fls.applications.append(prior_application)
        assert expected_output == test_candidate_applied_to_fls.most_recent_application().application_date


class TestGrade:
    def test_eligible_returns_correct_grades(self, test_session):
        assert ['Grade 7', 'Grade 6'] == [grade.value for grade in Grade.eligible('FLS')]
        assert ['Deputy Director (SCS1)'] == [grade.value for grade in Grade.eligible('SLS')]

    def test_new_grades_returns_correct_grades(self, test_session):
        current_grade = Grade(value='One below SCS', rank=5)
        promotion_roles = set([grade.value for grade in Grade.new_grades(current_grade)])
        assert promotion_roles == {'Grade 7', 'Grade 6', 'Deputy Director (SCS1)'}
        assert 'Admin Assistant (AA)' not in promotion_roles

    def test_new_grades_returns_grades_in_rank_order(self, test_session):
        current_grade = Grade(value='One below SCS', rank=5)
        promotion_roles = [grade.value for grade in Grade.new_grades(current_grade)]
        assert promotion_roles == ['Deputy Director (SCS1)', 'Grade 6', 'Grade 7']


class TestRole:

    @pytest.mark.parametrize("starting_grade, new_grade, temporary, expected_outcome", [
        ("Grade 7", "Grade 6", False, True),  # substantive promotion
        ("Grade 7", "Grade 7", None, False),  # level transfer
        ("Grade 6", "Grade 7", None, False),  # demotion
        ("Grade 7", "Grade 6", True, True),  # temporary promotion
    ])
    def test_is_promotion_returns_correct_values(self, starting_grade, new_grade, temporary, expected_outcome,
                                                 test_session, test_candidate):
        test_candidate.roles.extend([
            Role(date_started=date(2019, 1, 1), grade=Grade.query.filter_by(value=starting_grade).first(),
                 temporary_promotion=False),
            Role(date_started=date(2020, 6, 1), grade=Grade.query.filter_by(value=new_grade).first(),
                 temporary_promotion=temporary)
        ])
        assert test_candidate.roles[2].is_promotion() is expected_outcome
