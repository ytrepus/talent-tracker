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

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
