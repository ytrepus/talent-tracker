from flask import render_template, request, flash, redirect, current_app, url_for
from werkzeug.utils import secure_filename
from app.models import Candidate, FLSLeadership, SLSLeadership, db
from app.routes import route_blueprint
import os
import csv


UPDATE_TYPES = {"FLS": FLSLeadership, "SLS": SLSLeadership}
ALLOWED_TYPES = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_TYPES


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
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            with open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) as uploaded_csv:
                update_type = UPDATE_TYPES.get(request.form.get('update_type'))
                csv_reader = csv.DictReader(uploaded_csv, delimiter=',')
                for row in csv_reader:
                    db.session.add(update_type(**row))
                    db.session.commit()
    return ("Posted", 200)
