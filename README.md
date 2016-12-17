# Biolink API

## Getting Started

```
$ pyvenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ export PYTHONPATH=.:$PYTHONPATH
$ python rest_api_demo/app.py
```

to run:

```
python3 biolink/app.py
```

Then look at:

http://localhost:8888/api/

For the swagger docs

Note that only a small subset has been implemented

## Goals

This API will wrap and integrate number of different more modular APIs
and database engines or analysis services. The idea is that the API
implementation will do the right thing - for example, using Solr for
searches but injecting results with fast in-memory traversal of
ontology graphs.

This is a proof of concept implementation. May be implemented using a JVM language, e.g. scala in future.

## Notes

May bear some traces of where the code was initially copied from:
http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/
