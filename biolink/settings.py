import yaml
from os import path

# Flask settings
FLASK_SERVER_NAME = 'api.geneontology.org'
FLASK_DEBUG = True  # Do not use debug mode in production

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

def get_biolink_config():
    global biolink_config
    if biolink_config is None:
        with open(CONFIG, 'r') as f:
            biolink_config = yaml.load(f)
    return biolink_config

def get_route_mapping():
    global route_mapping
    if route_mapping is None:
        with open(ROUTES, 'r') as FH:
            route_mapping = yaml.load(FH)
    return route_mapping
