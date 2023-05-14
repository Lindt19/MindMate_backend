FROM python:3.8-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY . .

CMD [ "python", "app.py"]
