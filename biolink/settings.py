import yaml
import importlib
from os import path, environ

# Flask settings
FLASK_SERVER_NAME = 'localhost:8888'
# Do not use debug mode in production
FLASK_DEBUG = eval(environ['FLASK_DEBUG']) if 'FLASK_DEBUG' in environ else True
FLASK_USE_RELOADER = eval(environ['FLASK_USE_RELOADER']) if 'FLASK_USE_RELOADER' in environ else True

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# This is set to false to prevent Flask-Restplus from
# changing the error message structure
ERROR_INCLUDE_MESSAGE = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False

CONFIG = path.join(path.dirname(path.abspath(__file__)), '../conf/config.yaml')
ROUTES = path.join(path.dirname(path.abspath(__file__)), '../conf/routes.yaml')
biolink_config = None
route_mapping = None
identifier_converter = None

def get_biolink_config():
    global biolink_config
    if biolink_config is None:
        with open(CONFIG, 'r') as f:
            biolink_config = yaml.load(f, Loader=yaml.FullLoader)
    return biolink_config

def get_route_mapping():
    global route_mapping
    if route_mapping is None:
        with open(ROUTES, 'r') as FH:
            route_mapping = yaml.load(FH, Loader=yaml.FullLoader)
    return route_mapping

def get_identifier_converter():
    global identifier_converter
    if identifier_converter is None:
        module_name, class_name = get_biolink_config()['identifier_converter'].rsplit(".", 1)
        MyClass = getattr(importlib.import_module(module_name), class_name)
        identifier_converter = MyClass()
    return identifier_converter
