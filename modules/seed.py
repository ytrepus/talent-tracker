import random
from string import ascii_lowercase
from app.models import *
from datetime import date


def random_string(length: int) -> str:
    return ''.join([random.choice(ascii_lowercase) for i in range(length)])


def generate_random_fixed_data():

    choices = {
        'orgs': ["Ministry of", "Department of", "Their Majesty's"]
    }

    organisations = [f"{random.choice(choices['orgs'])} {random_string(16)}" for i in range(44)]
    professions = [f"{random_string(12)}".capitalize() for i in range(15)]
    locations = ["East Midlands", "East of England", "London", "North East England", "North West England",
                 "Northern Ireland", "Overseas", "Prefer not to say", "Scotland", "South East England",
                 "South West England", "Wales", "West Midlands", "Yorkshire & the Humber"]

    organisations = [Organisation(name=string) for string in organisations]
    organisations.append(Organisation(name='Cabinet Office'))
    grades = [
        'Prefer not to say',
        'AA – Administrative Assistant',
        'AO – Administrative Officer',
        'EO – Executive Officer',
        'HEO – Higher Executive Officer',
        'HEO (D) – Faststream',
        'SEO – Senior Executive Officer',
        'Grade 7',
        'Grade 6',
        'SCS1 – Deputy Director',
        'SCS2 – Director',
        'SCS3 – Director General',
        'SCS 4 – Permanent Secretary',
    ]
    grades.reverse()

    bame_ethnic_groups = [
        "Any other Asian background",
        "Any other Black/African/Caribbean background",
        "Any other Ethnic background",
        "Any other mixed/multiple ethnic background",
        "Arab",
        "Asian or Asian British - Bangladeshi",
        "Asian or Asian British - Chinese",
        "Asian or Asian British - Indian",
        "Asian or Asian British - Pakistani",
        "Black or Black British African",
        "Black or Black British Caribbean",
        "Mixed - White and Asian",
        "Mixed - White and Black African",
        "Mixed - White and Black Caribbean",
        "White - Gypsy or Irish Traveller",
    ]
    non_bame_ethnic_groups = [
        "Any other white background",
        "Prefer not to say",
        "White - Irish",
        "White English/Welsh/Scottish/Northern Irish/British",
    ]
    ethnic_groups = [Ethnicity(value=item, bame=True) for item in bame_ethnic_groups]
    ethnic_groups.extend([Ethnicity(value=item, bame=False) for item in non_bame_ethnic_groups])
    grades = [Grade(value=grade, rank=i) for i, grade in enumerate(grades)]
    professions = [Profession(value=string) for string in professions]
    locations = [Location(value=string) for string in locations]

    return {'organisations': organisations, 'grades': grades, 'professions': professions, 'locations': locations,
            'ethnicities': ethnic_groups, 'schemes': [Scheme(name='FLS'), Scheme(name='SLS')]}


def generate_known_candidate():
    return Candidate(
        email_address="staging.candidate@gov.uk", joining_date=date(2015, 9, 1),
        completed_fast_stream=True,
        joining_grade=Grade.query.filter(Grade.value.like("%Faststream%")).first().id,
        roles=[Role(date_started=date(2015, 9, 2), temporary_promotion=False,
                    organisation_id=Organisation.query.filter(Organisation.name == 'Cabinet Office').first().id,
                    grade=Grade.query.filter(Grade.value.like("%Faststream%")).first())
               ]
    )


def generate_random_candidate():
    return Candidate(email_address=f"{random_string(16)}@gov.uk",
                     joining_date=date(random.randrange(1960, 2018), random.randrange(1, 12), random.randrange(1, 28)),
                     completed_fast_stream=random.choice([True, False]),
                     joining_grade=(Grade.query.filter_by(rank=6).first()).id,
                     ethnicity_id=random.choice(Ethnicity.query.all()).id
                     )


def apply_candidate_to_scheme(scheme_name: str, candidate: Candidate):
    candidate.applications.append(
        Application(scheme_id=Scheme.query.filter_by(name=scheme_name).first().id, successful=True)
    )
    return candidate


def promote_candidate(candidate: Candidate, temporary=random.choice([True, False])):
    candidate.roles.extend([Role(date_started=date(2018, 1, 1), temporary_promotion=False),
                            Role(date_started=date(2019, 6, 1), temporary_promotion=temporary)])
    return candidate


def random_candidates(scheme: str, number: int):
    return [apply_candidate_to_scheme(scheme, generate_random_candidate()) for i in range(number)]


def commit_data():
    for key, value in generate_random_fixed_data().items():
        db.session.add_all(value)
    candidate = generate_known_candidate()
    db.session.add(candidate)
    random_promoted_fls_candidates = [promote_candidate(candidate) if i % 2 == 0 else candidate
                                      for i, candidate in enumerate(random_candidates('FLS', 100))]
    random_promoted_sls_candidates = [promote_candidate(candidate) if i % 2 == 0 else candidate
                                      for i, candidate in enumerate(random_candidates('SLS', 100))]
    candidates = random_promoted_sls_candidates + random_promoted_fls_candidates
    print(candidates)
    db.session.add_all(candidates)
    db.session.commit()


def clear_old_data():
    tables = [Application, Role, Candidate, Organisation, Profession, Grade, Location, Ethnicity, Scheme]
    for table in tables:
        table.query.delete()
        db.session.commit()
