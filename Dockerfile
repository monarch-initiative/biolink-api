FROM python:3.8-slim

WORKDIR /biolink-api

VOLUME /config

RUN apt-get -y update && apt-get install -y git curl

COPY requirements.txt ./
COPY wsgi.py ./
COPY logging.conf ./

COPY biolink ./biolink
COPY biowikidata ./biowikidata
COPY causalmodels ./causalmodels
COPY conf ./conf
COPY tests ./tests
COPY .git ./.git

RUN mkdir /biolink-api/scripts
COPY docker ./scripts

ENV PYTHONPATH "${PYTHONPATH}:/biolink-api"

ENV PATH="/biolink-api/scripts/:$PATH"

RUN pip install -r requirements.txt

COPY ./resources/biolink-config.yaml /biolink-api/conf/config.yaml
COPY ./resources/ontobio-config.yaml /usr/local/lib/python3.8/site-packages/ontobio/config.yaml

EXPOSE 5000
