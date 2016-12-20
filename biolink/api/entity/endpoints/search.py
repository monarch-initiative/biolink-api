import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('entity/search', description='Search for entities')

parser = api.parser()
parser.add_argument('subject_taxon', type=str, help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('attribute', action='append', help='positive attributes, e.g. ontology terms, to include in query')
parser.add_argument('negative_attribute', action='append', help='negative attributes, e.g. ontology terms, to exclude in query')
parser.add_argument('weighted_attribute', action='append', help='weighted attributes, specified as a range from 0 to 1 plus an ontology term, e.g. 0.3*HP:0000001')
parser.add_argument('noise', type=bool, help='If set, uses noise-tolerant querying, e.g owlsim, boqa')

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
    def get(self, search_term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []

@ns.route('/query/')
class Authocomplete(Resource):


    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, search_term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []
    
    
    

