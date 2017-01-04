import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('individual', description='Individual humans (including patients), or organisms')

parser = api.parser()
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

@ns.route('/<id>')
class Individual(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []

@ns.route('/pedigree/<id>')
class Pedigree(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []
    

    
    

