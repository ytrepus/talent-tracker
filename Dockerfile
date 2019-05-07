FROM python:3.7.3
COPY ./app /code/app
COPY ./node_modules/govuk-frontend/assets /code/assets
COPY ./static/main.css /code/static/css/
COPY assets/js /code/static/js
COPY requirements.txt /code/
COPY run.py /code/
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT flask run --host 0.0.0.0