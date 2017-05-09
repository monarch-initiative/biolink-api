import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import search_result
from biolink.api.restplus import api
from ontobio.golr.golr_query import GolrSearchQuery
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('search', description='Search for entities')

def get_simple_parser():
        """
        A simple flaskrest parser object that includes basic http params
        """
        p = api.parser()
        p.add_argument('taxon', type=str, help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
        p.add_argument('category', action='append', help='e.g. gene, disease')
        p.add_argument('subclass_of', action='append', help='restrict search to entities that are subclasses of the specified class')
        p.add_argument('engine', help='Name of engine to perform search')
        p.add_argument('rows', type=int, required=False, default=20, help='number of rows')
        return p

def get_advanced_parser():
        """
        Extends simple flaskrest parser object with params
        """
        p = get_simple_parser()
        p.add_argument('attribute', action='append', help='positive attributes, e.g. ontology terms, to include in query')
        p.add_argument('negative_attribute', action='append', help='negative attributes, e.g. ontology terms, to exclude in query')
        p.add_argument('weighted_attribute', action='append', help='weighted attributes, specified as a range from 0 to 1 plus an ontology term, e.g. 0.3*HP:0000001')
        p.add_argument('noise', type=bool, help='If set, uses noise-tolerant querying, e.g owlsim, boqa')
        return p

def search(term, args):
    q = GolrSearchQuery(term, args)
    return q.exec()
    
simple_parser = get_simple_parser()
adv_parser = get_advanced_parser()

@ns.route('/entity/<term>')
@api.doc(params={'term': 'search string, e.g. shh, parkinson, femur'})
class SearchEntities(Resource):

    @api.expect(simple_parser)

    #@api.marshal_list_with(search_result)
    def get(self, term):
        """
        Returns list of matching concepts or entities using lexical search
        """
        args = simple_parser.parse_args()
        q = GolrSearchQuery(term,
                            category=args.category)
        results = q.exec()
        return results

@ns.route('/entity/autocomplete/<term>')
class Autocomplete(Resource):

    @api.expect(simple_parser)
    def get(self, search_term):
        """
        Returns list of matching concepts or entities using lexical search
        """
        args = parser.parse_args()

        return []

#@ns.route('/entity/query/')
#class BooleanQuery(Resource):
#
#    @api.expect(adv_parser)
#    def get(self, search_term):
#        """
#        Returns list of matches based on 
#        """
#        args = parser.parse_args()
#
#        return []
    
    
    

