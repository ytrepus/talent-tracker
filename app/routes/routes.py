from flask import render_template, request, url_for, redirect, session
from app.models import Candidate, Grade, db, Role, Organisation, Location, Profession
from app.routes import route_blueprint
from datetime import date


@route_blueprint.route('/')
def hello_world():
    return render_template('index.html')


@route_blueprint.route('/hello')
def hello():
    return 'Hello world'


@route_blueprint.route('/results')
def results():
    candidates = Candidate.query.all()
    return render_template('results.html', candidates=candidates, heading='Search results', accordion_data=[
        {'heading': 'Heading', 'content': 'Lorem ipsum, blah blah'}
    ])


@route_blueprint.route('/update', methods=["POST", "GET"])
def choose_update():
    next_steps = {
        'role': 'route_blueprint.search_candidate'
    }
    if request.method == "POST":
        session['bulk-single'] = request.form.get("bulk-single")
        session['update-type'] = request.form.get("update-type")
        return redirect(url_for(next_steps.get(request.form.get("update-type"))))
    return render_template('choose-update.html')


@route_blueprint.route('/update/search-candidate', methods=["POST", "GET"])
def search_candidate():
    if request.method == "POST":
        try:
            candidate_id = Candidate.query.filter_by(personal_email=request.form.get('candidate-email')).one_or_none().id
        except AttributeError:
            session['error'] = "That email does not exist"
            return redirect(url_for('route_blueprint.search_candidate'))
        return redirect(url_for('route_blueprint.update', bulk_or_single=session.get('bulk-single'),
                                update_type=session.get('update-type'), candidate_id=candidate_id))
    return render_template('search-candidate.html', error=session.pop('error', None))


@route_blueprint.route('/update/<string:bulk_or_single>/<string:update_type>/<int:candidate_id>', methods=["POST", "GET"])
def update(bulk_or_single, update_type, candidate_id=None):
    if not candidate_id:
        return redirect(url_for('route_blueprint.search_candidate'))
    candidate = Candidate.query.get(candidate_id)
    if request.method == 'POST':
        form_dict = {k: int(v[0]) for k, v in request.form.to_dict(flat=False).items()}
        db.session.add(Role(
            date_started=date(
                year=form_dict.get('start-date-year'), month=form_dict.get('start-date-month'),
                day=form_dict.get('start-date-day')
            ),
            organisation_id=form_dict.get('new-org'), candidate_id=candidate.id,
            profession_id=form_dict.get('new-profession'), location_id=form_dict.get('new-location'),
            grade_id=form_dict.get('new-grade'), temporary_promotion=bool(form_dict.get('temporary-promotion'))
        ))
        db.session.commit()
        return redirect(url_for('route_blueprint.complete'))
    update_types = {
        "role": {'title': "Role update", "promotable_grades": Grade.new_grades(Grade(value='Grade name', rank=7)),
                 "organisations": Organisation.query.all(), "locations": Location.query.all(),
                 "professions": Profession.query.all()
                 },
        "fls-survey": "FLS Survey update", "sls-survey": "SLS Survey update"
    }
    template = f"updates/{bulk_or_single}-{update_type}.html"
    return render_template(template, page_header=update_types.get(update_type).get('title'),
                           data=update_types.get(update_type), candidate=candidate)


@route_blueprint.route('/update/email-address', methods=["POST", "GET"])
def email_address():
    if request.method == "POST":
        if request.form.get("update-email-address") == "true":
            session['new-email'] = request.form.get("new-email-address")
            candidate = Candidate.query.get(session.get('candidate-id'))
            candidate.personal_email = request.form.get("new-email-address")
            db.session.add(candidate)
            db.session.commit()

        return redirect(url_for('route_blueprint.complete'))

    return render_template('updates/email-address.html')


@route_blueprint.route('/update/complete', methods=["GET"])
def complete():
    return render_template('updates/complete.html')
