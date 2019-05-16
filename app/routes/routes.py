from flask import render_template
from app.models import Candidate
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

@route_blueprint.route('/update/bulk', methods=['POST', 'GET'])
def update_bulk():
    return ("Posted", 200)