import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('owl/ontology', description='OWL-level operations on an ontology')

parser = api.parser()
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

@ns.route('/dlquery/<query>')
class DLQuery(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, query):
        """
        Placeholder - use OWLery for now
        """
        args = parser.parse_args()

        return []

@ns.route('/sparql/<query>')
class SparqlQuery(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, query):
        """
        Placeholder - use direct SPARQL endpoint for now
        """
        args = parser.parse_args()

        return []
    

    
    

