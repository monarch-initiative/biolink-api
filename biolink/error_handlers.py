from prefixcommons.curie_util import InvalidSyntax, NoExpansion, NoContraction, NoPrefix, AmbiguousPrefix

from biolink.api.restplus import api
from biolink import settings
import logging

class CustomException(Exception):
    def __init__(self, message, status_code=500, debug=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if settings.FLASK_DEBUG:
            self.debug = debug

    def to_dict(self):
        return {
            'error': {
                'message': self.message,
                'code': self.status_code,
                'debug': dict(self.debug or ())
            }
        }

class NoResultFoundException(CustomException):
    """
    Use this exception when results are expected but no result found
    """
    def __init__(self, message, status_code=404, debug=None):
        CustomException.__init__(self, message, status_code, debug)

class UnrecognizedBioentityTypeException(CustomException):
    """
    Use this exception when encountering an unrecognized Bioentity type
    """
    def __init__(self, message, status_code=400, debug=None):
        CustomException.__init__(self, message, status_code, debug)

class RouteNotImplementedException(CustomException):
    """
    Use this exception for routes that have yet to be implemented
    """
    def __init__(self, message=None, status_code=500, debug=None):
        if not message:
            message = 'Route not yet implemented'
        CustomException.__init__(self, message, status_code, debug)

class UnhandledException(CustomException):
    """
    Use this exception if its unclear which exception to raise
    """
    def __init__(self, message, status_code=500, debug=None):
        CustomException.__init__(self, message, status_code, debug)

@api.errorhandler
def default_error_handler(e):
    """
    Default error handler
    """
    status_code = 500
    message = 'An exception occurred: {}'.format(e)
    logging.error(message)
    return {
        'error': {
            'message': message,
            'code': status_code
        }
    }, status_code

@api.errorhandler(NoResultFoundException)
def no_result_found_exception_handler(e):
    """
    Error handler to handle NoResultFoundException
    """
    message = e.message
    logging.error(message)
    return e.to_dict(), e.status_code

@api.errorhandler(UnrecognizedBioentityTypeException)
def unrecognized_bioentity_type_exception(e):
    """
    Error handler to handle UnrecognizedBioentityTypeException
    """

    message = e.message
    logging.error(message)
    return e.to_dict(), e.status_code

@api.errorhandler(RouteNotImplementedException)
def route_not_implemented_exception(e):
    """
    Error handler to handle RouteNotImplementedException
    """
    message = e.message
    logging.error(message)
    return e.to_dict(), e.status_code

@api.errorhandler(UnhandledException)
def unhandled_exception_handler(e):
    """
    Error handler to handle UnhandledException
    """
    message = e.message
    logging.error(message)
    return e.to_dict(), e.status_code

@api.errorhandler(InvalidSyntax)
def invalid_syntax_exception_handler(e):
    """
    Error handler to handle InvalidSyntax
    """
    message = 'Invalid syntax for CURIE {}'.format(e.id)
    logging.error(message)
    return {
        'error': {
            'message': message,
            'code': 400
        }
    }, 400

@api.errorhandler(NoExpansion)
def no_expansion_exception_handler(e):
    """
    Error handler to handle NoExpansion
    """
    message = 'No expansion for {}'.format(e.id)
    logging.error(message)
    return {
        'error': {
            'message': message,
            'code': 400
        }
    }, 400

@api.errorhandler(NoContraction)
def no_contraction_exception_handler(e):
    """
    Error handler to handle NoContraction
    """
    message = 'No contraction for URI {}'.format(e.uri)
    logging.error(message)
    return {
        'error': {
            'message': message,
            'code': 400
        }
    }, 400

@api.errorhandler(NoPrefix)
def no_prefix_exception_handler(e):
    """
    Error handler to handle NoPrefix
    """
    message = 'No prefix for URI {}'.format(e.uri)
    logging.error(message)
    return {
        'error': {
            'message': message,
            'code': 400
        }
    }, 400

@api.errorhandler(AmbiguousPrefix)
def ambiguous_prefix_exception_handler(e):
    """
    Error handler to handle AmbiguousPrefix
    """
    message = 'Ambiguous prefix for URI {}'.format(e.uri)
    logging.error(message)
    return {
        'error': {
            'message': message,
            'code': 400
        }
    }, 400
