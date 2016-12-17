import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from biolink.util.golr_associations import get_associations
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('entity/search', description='Search for entities')

parser = api.parser()
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

@ns.route('/<term>')
class SearchEntities(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []

@ns.route('/autocomplete/<term>')
class Authocomplete(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, search_term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []

    
    

