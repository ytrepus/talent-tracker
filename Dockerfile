FROM python:3.7.3
COPY . /code
WORKDIR /code
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT python ./app.py