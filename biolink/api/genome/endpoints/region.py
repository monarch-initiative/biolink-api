import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import sequence_feature
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('genome/features/', description='Operations to retrieve sequence features')

parser = api.parser()

@ns.route('/within/<build>/<reference>/<begin>/<end>')
class FeaturesWithinResource(Resource):

    
    @api.marshal_list_with(sequence_feature)
    @api.expect(parser)
    def get(self, build, reference, begin, end):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []


    
    

