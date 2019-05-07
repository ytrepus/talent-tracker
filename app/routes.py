from flask import render_template
from app import app
from app.models import Candidate


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/hello')
def hello():
    return 'Hello world'


@app.route('/results')
def results():
    candidates = Candidate.query.all()
    return render_template('results.html', candidates=candidates)
