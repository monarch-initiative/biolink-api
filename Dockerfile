FROM python:3.7-slim

WORKDIR /biolink-api

VOLUME /config

RUN apt-get -y update && apt-get install -y git curl

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

RUN mkdir /biolink-api/scripts
COPY docker ./scripts

ENV PYTHONPATH "${PYTHONPATH}:/biolink-api"

ENV PATH="/biolink-api/scripts/:$PATH"

RUN pip install -r requirements.txt

EXPOSE 5000
