FROM python:3.7.3
COPY . /code
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt
RUN pwd && ls
ENTRYPOINT python ./app.py