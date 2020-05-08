import logging
import traceback

from flask_restplus import Api
from biolink import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

api = Api(version='1.0.1', title='BioLink API',
          license='BSD3',
          contact='info@monarchinitiative.org',
          description='API integration layer for linked biological objects.\n\n __Source:__ https://github.com/biolink/biolink-api/')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404
