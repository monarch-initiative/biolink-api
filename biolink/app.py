import logging.config
import os, importlib
from flask import Flask, Blueprint, request
from flask import render_template
from flask_cors import CORS, cross_origin
from biolink import settings
from biolink.api.restplus import api
from biolink.database import db

logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)

config = settings.get_biolink_config()
module_list = config.get('biolink_modules')

for module in module_list:
    try:
        m = importlib.import_module(module)
        ns = getattr(m, 'ns')
    except ImportError:
        log.error("Cannot import module: {}".format(module))


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


blueprint = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint)
#api.add_namespace(link_search_namespace)
app.register_blueprint(blueprint)
db.init_app(app)

# initial setup
#from ontobio.ontol_factory import OntologyFactory
#factory = OntologyFactory()
#ont = factory.create()


@app.route("/")
def hello():
    return render_template('index.html', base_url=request.base_url)

def main():
    #initialize_app(app)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=settings.FLASK_DEBUG)

if __name__ == "__main__":
    main()
