import random
from string import ascii_lowercase
from app import create_app
from app.models import *
from datetime import date

create_app()


def random_string(length: int) -> str:
    return ''.join([random.choice(ascii_lowercase) for i in range(length)])


def generate_random_fixed_data():

    choices = {
        'orgs': ["Ministry of", "Department of", "Their Majesty's"]
    }

    organisations = [f"{random.choice(choices['orgs'])} {random_string(16)}" for i in range(450)]
    grades = [f"Grade {i}" for i in range(12)]
    professions = [f"{random_string(12)}".capitalize() for i in range(15)]
    locations = ["East Midlands", "East of England", "London", "North East England", "North West England",
                 "Northern Ireland", "Overseas", "Prefer not to say", "Scotland", "South East England",
                 "South West England", "Wales", "West Midlands", "Yorkshire & the Humber"]

    organisations = [Organisation(name=string) for string in organisations]
    grades = [Grade(value=string, rank=i) for string, i in enumerate(grades)]
    professions = [Profession(value=string) for string in professions]
    locations = [Location(value=string) for string in locations]

    return {'organisations': organisations, 'grades': grades, 'professions': professions, 'locations': locations}


def generate_random_candidate():
    return Candidate(personal_email=f"{random_string(8)}@gov.uk",
                     joining_date=date(random.randrange(1960, 2018), random.randrange(1, 12), random.randrange(1, 28)),
                     completed_fast_stream=random.choice([True, False]),
                     joining_grade=random.choice(Grade.query.all()).id
                     )


def commit_data():
    for key, value in generate_random_fixed_data().items():
        db.session.add_all(value)
    db.session.add(generate_random_candidate())
    db.session.commit()


def clear_old_data():
    tables = [Role, Candidate, Organisation, Profession, Grade, Location]
    for table in tables:
        table.query.delete()
        db.session.commit()
