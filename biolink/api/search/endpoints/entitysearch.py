import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import search_result
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('search/entity', description='Search for entities')

parser = api.parser()
parser.add_argument('taxon', type=str, help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('category', action='append', help='e.g. gene, disease')
parser.add_argument('subclass_of', action='append', help='restrict search to entities that are subclasses of the specified class')
parser.add_argument('attribute', action='append', help='positive attributes, e.g. ontology terms, to include in query')
parser.add_argument('negative_attribute', action='append', help='negative attributes, e.g. ontology terms, to exclude in query')
parser.add_argument('weighted_attribute', action='append', help='weighted attributes, specified as a range from 0 to 1 plus an ontology term, e.g. 0.3*HP:0000001')
parser.add_argument('noise', type=bool, help='If set, uses noise-tolerant querying, e.g owlsim, boqa')
parser.add_argument('engine', help='Name of engine to perform search')

@ns.route('/<term>')
@api.doc(params={'term': 'search string, e.g. shh, parkinson, femur'})
class SearchEntities(Resource):

    @api.expect(parser)

    @api.marshal_list_with(search_result)
    def get(self, term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []

@ns.route('/autocomplete/<term>')
class Authocomplete(Resource):

    @api.expect(parser)
    def get(self, search_term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []


    
    
    

