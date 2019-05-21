from flask import render_template, request, url_for, redirect
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
    if request.method == "POST":
        return redirect(url_for('route_blueprint.update', bulk_or_single=request.form.get("bulk-single"),
                                update_type=request.form.get("update-type")))
    return render_template('choose_update.html')

@route_blueprint.route('/update/<string:bulk_or_single>/<string:update_type>')
def update(bulk_or_single, update_type):
    update_types = {
        "role": {'title': "Role update", "promotable_grades": Grade.promotion_roles(Grade(value='Grade name', rank=7))},
        "fls-survey": "FLS Survey update", "sls-survey": "SLS Survey update"
    }
    template = f"updates/{bulk_or_single}-{update_type}.html"
    return render_template(template, page_header=update_types.get(update_type))
