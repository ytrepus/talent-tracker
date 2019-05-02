FROM python:3.7.3
COPY ./app /code/app
COPY ./node_modules/govuk-frontend /code/assets/govuk-frontend
COPY ./static /code/static
COPY requirements.txt /code/
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT flask run --host 0.0.0.0