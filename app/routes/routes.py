from flask import render_template, request, url_for, redirect, session
from app.models import Candidate, Grade, db, Organisation, Location, Profession
from app.routes import route_blueprint


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
        candidate = Candidate.query.filter_by(personal_email=request.form.get('candidate-email')).one_or_none()
        if candidate:
            session['candidate-id'] = candidate.id
        else:
            session['error'] = "That email does not exist"
            return redirect(url_for('route_blueprint.search_candidate'))
        return redirect(url_for('route_blueprint.update', bulk_or_single=session.get('bulk-single'),
                                update_type=session.get('update-type')))
    return render_template('search-candidate.html', error=session.pop('error', None))


@route_blueprint.route('/update/<string:bulk_or_single>/<string:update_type>', methods=["POST", "GET"])
def update(bulk_or_single, update_type):
    candidate_id = session.get('candidate-id')
    if not candidate_id:
        return redirect(url_for('route_blueprint.search_candidate'))

    if request.method == 'POST':
        session['new-role'] = {key: int(value[0]) for key, value in request.form.to_dict(flat=False).items()}
        return redirect(url_for('route_blueprint.complete'))

    update_types = {
        "role": {'title': "Role update",
                 "promotable_grades": Grade.new_grades(Candidate.query.get(candidate_id).current_grade()),
                 "organisations": Organisation.query.all(), "locations": Location.query.all(),
                 "professions": Profession.query.all()
                 },
        "fls-survey": "FLS Survey update", "sls-survey": "SLS Survey update"
    }
    template = f"updates/{bulk_or_single}-{update_type}.html"
    return render_template(template, page_header=update_types.get(update_type).get('title'),
                           data=update_types.get(update_type), candidate=Candidate.query.get(candidate_id))


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
