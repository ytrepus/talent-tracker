from flask import render_template, request, url_for, redirect, session
from app.models import Candidate, Grade
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
        session['candidate-email'] = request.form.get('candidate-email')
        return redirect(url_for('route_blueprint.update', bulk_or_single=session.get('bulk-single'),
                                update_type=session.get('update-type')))
    return render_template('search-candidate.html')


@route_blueprint.route('/update/<string:bulk_or_single>/<string:update_type>')
def update(bulk_or_single, update_type):
    candidate = Candidate.query.filter_by(personal_email=session.get('candidate-email')).one_or_none()
    # TODO: if candidate doesn't exist, return user to search page
    update_types = {
        "role": {'title': "Role update", "promotable_grades": Grade.promotion_roles(Grade(value='Grade name', rank=7))},
        "fls-survey": "FLS Survey update", "sls-survey": "SLS Survey update"
    }
    template = f"updates/{bulk_or_single}-{update_type}.html"
    return render_template(template, page_header=update_types.get(update_type).get('title'),
                           data=update_types.get(update_type), candidate=candidate)
