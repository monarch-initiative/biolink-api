FROM python:3.7-slim

WORKDIR biolink-api

RUN apt-get -y update && apt-get install -y git

COPY requirements.txt ./
COPY wsgi.py ./
COPY logging.conf ./

COPY biolink ./biolink
COPY biomodel ./biomodel
COPY biowikidata ./biowikidata
COPY causalmodels ./causalmodels
COPY conf ./conf
COPY scigraph ./scigraph
COPY tests ./tests
COPY .git ./.git

ENV PYTHONPATH "${PYTHONPATH}:/biolink-api"

RUN pip install -r requirements.txt

EXPOSE 5000
