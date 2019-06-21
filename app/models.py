from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.ext.declarative import declared_attr


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


class CandidateGetterMixin:
    @declared_attr
    def candidates(cls):
        return db.relationship("Candidate", backref=cls.__name__.lower())


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def check_password(self, password_to_check: str) -> bool:
        return check_password_hash(self.password_hash, password_to_check)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User {}>'.format(self.email)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Ethnicity(CandidateGetterMixin, db.Model):
    """
    The ethnicity table has a boolean flag for bame, allowing us to query candidates (and therefore data connected to
    candidates) according to ethnicity at a broad, BAME level
    """
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512))
    bame = db.Column(db.Boolean)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joining_date = db.Column(db.Date())
    completed_fast_stream = db.Column(db.Boolean())
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    email_address = db.Column(db.String(120), unique=True)

    # protected characteristics
    caring_responsibility = db.Column(db.Boolean())  # TRUE: yes, FALSE: no, NULL: Prefer not to say
    long_term_health_condition = db.Column(db.Boolean())

    age_range_id = db.Column(db.ForeignKey('age_range.id'), nullable=False, default=1)
    working_pattern_id = db.Column(db.ForeignKey('working_pattern.id'))
    belief_id = db.Column(db.ForeignKey('belief.id'))
    sexuality_id = db.Column(db.ForeignKey('sexuality.id'))
    gender_id = db.Column(db.ForeignKey('gender.id'))
    ethnicity_id = db.Column(db.ForeignKey('ethnicity.id'))

    joining_grade = db.Column(db.ForeignKey('grade.id'))

    roles = db.relationship('Role', backref='candidate', lazy='dynamic')
    applications = db.relationship('Application', backref='candidate', lazy='dynamic')

    def __repr__(self):
        return f'<Candidate email {self.email_address}>'

    def current_grade(self) -> 'Grade':
        return self.roles.order_by(Role.date_started.desc()).first().grade

    def promoted(self, promoted_after_date: datetime.date, temporary=False):
        """
        Returns whether this candidate was promoted after the passed date. Promotions are only considered if they're
        substantive. There is a flag is users want to see temporary promotions instead
        :param promoted_after_date:
        :type promoted_after_date:
        :param temporary: Whether the user wants temporary or substantive promotions
        :type temporary: bool
        :return:
        :rtype:
        """
        roles_after_date = self.roles.filter(and_(
            Role.date_started >= promoted_after_date,
            Role.temporary_promotion.is_(temporary),
        )).order_by(Role.date_started.desc()).all()
        return len(roles_after_date) > 0

    def current_scheme(self) -> 'Scheme':
        return Scheme.query.get(self.applications.order_by(Application.application_date.desc()).first().scheme_id)


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
    rank = db.Column(db.Integer, nullable=False)

    @staticmethod
    def eligible(scheme: str):
        """
        This method returns those Grades that are eligible for specific schemes.
        :param scheme: name of the scheme
        :type scheme: str
        :return: A list of eligible Grades
        :rtype: List[Grade]
        """
        if scheme == 'FLS':
            eligible_grades = Grade.query.filter(Grade.value.like('Grade%')).all()
        else:
            eligible_grades = Grade.query.filter(Grade.value.like('Deputy%'))
        return eligible_grades

    @staticmethod
    def new_grades(current_grade: 'Grade'):
        """
        Grades that are one below, equal to, or more senior than, `current_grade`. We include grades one below because
        candidates may be coming off temporary promotion. Remember that the more senior the role, the lower the rank
        value!
        :param current_grade: Grade object, describing the current Grade of Candidate
        :type current_grade: Grade
        :return: A list of grades more senior or at the same level
        :rtype: List[Grade]
        """
        current_rank = current_grade.rank
        return Grade.query.filter(Grade.rank <= (current_rank + 1)).order_by(Grade.rank.asc()).all()

    def __repr__(self):
        return f"Grade {self.value}"


class Profession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(256))


class Location(db.Model):
    """
    The location_tag value is for one of four values: London, Region, Overseas, or Devolved. This allows for easier
    data retrieval when searching for promotions or applications from a broad space
    """
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))
    location_tag = db.Column(db.String(16), index=True)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_started = db.Column(db.Date())
    temporary_promotion = db.Column(db.Boolean(), default=None)

    organisation_id = db.Column(db.ForeignKey('organisation.id'))
    candidate_id = db.Column(db.ForeignKey('candidate.id'))
    profession_id = db.Column(db.ForeignKey('profession.id'))
    location_id = db.Column(db.ForeignKey('location.id'))
    grade_id = db.Column(db.ForeignKey('grade.id'))

    grade = db.relationship('Grade', lazy='select')

    def __repr__(self):
        return f'<Role held by {self.candidate} at {self.organisation_id}>'

    def is_promotion(self):
        role_before_this = self.candidate.roles.order_by(Role.date_started.desc()).first()
        return self.grade.rank > role_before_this.grade.rank and not self.temporary_promotion


class Scheme(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16))


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    aspirational_grade = db.Column(db.ForeignKey('grade.id'))
    scheme_id = db.Column(db.ForeignKey('scheme.id'))
    candidate_id = db.Column(db.ForeignKey('candidate.id'), nullable=False)

    application_date = db.Column(db.Date())
    scheme_start_date = db.Column(db.Date(), index=True)
    per_id = db.Column(db.Integer())
    employee_number = db.Column(db.String(25))
    successful = db.Column(db.Boolean())
    meta = db.Column(db.Boolean, default=False)
    delta = db.Column(db.Boolean, default=False)
    cohort = db.Column(db.Integer, unique=False)
    withdrawn = db.Column(db.Boolean(), default=False)


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


class AgeRange(CandidateGetterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(10))


class WorkingPattern(CandidateGetterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Belief(CandidateGetterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Gender(CandidateGetterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))


class Sexuality(CandidateGetterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128))
