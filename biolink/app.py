#!/usr/bin/env python

import logging.config
from os import path

import flask as f
from flask import Flask, Blueprint, request
from flask import render_template
from flask_cors import CORS, cross_origin
from biolink import settings
from biolink.ontology.ontology_manager import get_ontology

from biolink.api.restplus import api

from biolink.database import db

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)
log_file_path = path.join(path.dirname(path.abspath(__file__)), '../logging.conf')
logging.config.fileConfig(log_file_path)
log = logging.getLogger(__name__)


#def configure_app(flask_app):
#app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
app.config['ERROR_INCLUDE_MESSAGE'] = settings.ERROR_INCLUDE_MESSAGE

#def initialize_app(flask_app):
#    configure_app(flask_app)

blueprint = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint)

mapping = settings.get_route_mapping().get('route_mapping')

for ns in mapping['namespace']:
    namespace = api.namespace(ns['name'], description=ns['description'])
    routes = ns['routes']
    for r in routes:
        route = r['route']
        resource = r['resource']
        log.debug("Registering Resource: {} to route: {}".format(resource, route))
        module_name = '.'.join(resource.split('.')[0:-1])
        resource_class_name = resource.split('.')[-1]
        module = __import__(module_name, fromlist=[resource_class_name])
        resource_class = getattr(module, resource_class_name)
        namespace.add_resource(resource_class, route)

app.register_blueprint(blueprint)
db.init_app(app)

def preload_ontologies():
    ontologies = settings.get_biolink_config().get('ontologies')
    for ontology in ontologies:
        handle = ontology['handle']
        if ontology['pre_load']:
            log.info("Loading {}".format(ontology['id']))
            get_ontology(handle)

@app.route("/")
def hello():
    return render_template('index.html', base_url=request.base_url)

def main():
    #initialize_app(app)
    preload_ontologies()
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=settings.FLASK_DEBUG, use_reloader=settings.FLASK_USE_RELOADER)

if __name__ == "__main__":
    main()
