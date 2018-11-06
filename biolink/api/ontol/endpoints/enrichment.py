import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('bioentity_ids', help='List of ids')

class Foo(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self):
        """
        Maps to slim
        """
        args = parser.parse_args()

        return []


    
    

