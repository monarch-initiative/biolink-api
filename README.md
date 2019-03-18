# Gene Ontology API

The Gene Ontology API instance is accessible here:

https://api.geneontology.org/api/

Is is an implementation of both the [BioLink Model](https://github.com/biolink/biolink-model) and [BioLink Implementation](https://github.com/biolink/biolink-api) which rely on [Ontobio](https://github.com/biolink/ontobio)

## Running the server

After checking out this repo:

```
./start-server.sh
```

This uses gunicorn and starts a server on 8888 by default. pyvenv is
activated automatically.

Then look at:

http://localhost:8888/api/

For the swagger docs

To run in development mode:

```
pyvenv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.:$PYTHONPATH
python biolink/app.py
```



