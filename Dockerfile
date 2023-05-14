FROM python:3.8-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt /code

RUN pip install -r /code/requirements.txt

RUN python -m spacy download en_core_web_sm

COPY ./data /code/data

COPY . /code

CMD [ "python", "app.py"]

