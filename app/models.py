from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personal_email = db.Column(db.String(120), unique=True)
    joining_date = db.Column(db.Date())
    completed_fast_stream = db.Column(db.Boolean())

    joining_grade = db.Column(db.ForeignKey('grade.id'))

    roles = db.relationship('Role', backref='candidate', lazy='dynamic')
    applications = db.relationship('Application', backref='candidate', lazy='dynamic')

    def __repr__(self):
        return f'<Candidate email {self.personal_email}>'


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    parent_organisation_id = db.Column(db.ForeignKey('organisation.id'), unique=False)
    department = db.Column(db.Boolean())
    arms_length_body = db.Column(db.Boolean())

    roles = db.relationship('Role', backref='organisation', lazy='dynamic')

    def __repr__(self):
        return f'<Org {self.name}>'


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50))


class Profession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(256))


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_started = db.Column(db.Date())
    rank = db.Column(db.Integer)

    organisation_id = db.Column(db.ForeignKey('organisation.id'))
    candidate_id = db.Column(db.ForeignKey('candidate.id'))
    profession_id = db.Column(db.ForeignKey('profession.id'))
    location_id = db.Column(db.ForeignKey('location.id'))
    grade_id = db.Column(db.ForeignKey('grade.id'))

    grade = db.relationship('Grade', lazy='select')

    def __repr__(self):
        return f'<Role held by {self.candidate} at {self.organisation_id}>'


class Scheme(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16))


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    aspirational_grade = db.Column(db.ForeignKey('grade.id'))
    scheme_id = db.Column(db.ForeignKey('scheme.id'))
    candidate_id = db.Column(db.ForeignKey('candidate.id'), nullable=False)
    changeable_protected_characteristics = db.Column(db.ForeignKey('changeable_protected_characteristics.id'))

    application_date = db.Column(db.Date())
    scheme_start_date = db.Column(db.Date(), index=True)
    per_id = db.Column(db.Integer())
    employee_number = db.Column(db.String(25))
    successful = db.Column(db.Boolean())

    @validates('candidate_id')
    def validate_candidate_is_employed(self, key, candidate_id):
        candidate = Candidate.query.get(candidate_id)
        current_role = candidate.roles.filter(Role.date_started < self.application_date).\
            one_or_none()
        if current_role is not None:
            return candidate_id
        else:
            raise AssertionError("This candidate is not employed!")


class Leadership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confident_leader = db.Column(db.Integer())
    inspiring_leader = db.Column(db.Integer())
    when_new_role = db.Column(db.String(256))
    confidence_built = db.Column(db.Integer())

    application_id = db.Column(db.ForeignKey('application.id'), nullable=False)

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'leadership',
        'polymorphic_on': type
    }


class FLSLeadership(Leadership):
    id = db.Column(db.Integer(), db.ForeignKey('leadership.id'), primary_key=True)
    increased_visibility = db.Column(db.Integer())

    __mapper_args__ = {
        'polymorphic_identity': 'fls_leadership',
    }


class SLSLeadership(Leadership):
    id = db.Column(db.Integer(), db.ForeignKey('leadership.id'), primary_key=True)
    work_differently = db.Column(db.Integer())
    using_tools = db.Column(db.Integer())
    feel_ready = db.Column(db.Integer())

    __mapper_args__ = {
        'polymorphic_identity': 'sls_leadership',
    }


class QualificationLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class MainJobType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512))


class SchoolType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(256))


class IncomeEarnerEmployeeStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512))


class SupervisedOthers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512))


class FreeSchoolMeals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512))


class SocioEconomic(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    self_identify_lower_socio_economic_background = db.Column(db.String(256))

    candidate_id = db.Column(db.ForeignKey('candidate.id'))
    school_id = db.Column(db.ForeignKey('school_type.id'))
    qualification_level_id = db.Column(db.ForeignKey('qualification_level.id'))
    main_job_type_id = db.Column(db.ForeignKey('main_job_type.id'))
    income_earner_employee_status_id = db.Column(db.ForeignKey('income_earner_employee_status.id'))
    supervised_others_id = db.Column(db.ForeignKey('supervised_others.id'))
    free_school_meals_id = db.Column(db.ForeignKey('free_school_meals.id'))


class AgeRange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(10))


class WorkingPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Belief(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Gender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Sexuality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class ChangeableProtectedCharacteristics(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    caring_responsibility = db.Column(db.Boolean())  # TRUE: yes, FALSE: no, NULL: Prefer not to say
    long_term_health_condition = db.Column(db.Boolean())

    age_range_id = db.Column(db.ForeignKey('age_range.id'), nullable=False)
    application_id = db.Column(db.ForeignKey('application.id'))
    working_pattern_id = db.Column(db.ForeignKey('working_pattern.id'))
    belief_id = db.Column(db.ForeignKey('belief.id'))
    sexuality_id = db.Column(db.ForeignKey('sexuality.id'))
    gender_id = db.Column(db.ForeignKey('gender.id'))

