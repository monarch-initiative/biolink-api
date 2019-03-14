import logging

from flask_restplus import Resource
from biolink.datamodel.serializers import sequence_feature
from biolink.api.restplus import api

from biolink.error_handlers import RouteNotImplementedException

log = logging.getLogger(__name__)

parser = api.parser()

class FeaturesWithinResource(Resource):

    
    @api.marshal_list_with(sequence_feature)
    @api.expect(parser)
    def get(self, build, reference, begin, end):
        """
        Returns list of matches
        """
        args = parser.parse_args()
        raise RouteNotImplementedException()
