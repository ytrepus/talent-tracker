from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personal_email = db.Column(db.String(120), unique=True)
    date_of_birth = db.Column(db.Date(), index=True)
    scheme = db.Column(db.String(10))
    scheme_start_date = db.Column(db.Date(), index=True)

    roles = db.relationship('Role', backref='candidate', lazy='dynamic')

    def __repr__(self):
        return f'<Candidate email {self.personal_email}>'


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)

    roles = db.relationship('Role', backref='organisation', lazy='dynamic')

    def __repr__(self):
        return f'<Org {self.name}>'


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.ForeignKey('organisation.id'))
    candidate_id = db.Column(db.ForeignKey('candidate.id'))
    date_started = db.Column(db.Date())

    def __repr__(self):
        return f'<Role held by {self.candidate} at {self.organisation_id}>'
