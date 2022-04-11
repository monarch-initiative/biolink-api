import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from ontobio.sparql.sparql_ontol_utils import batch_fetch_ids
import pysolr

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('label', action='append', help='List of labels', required=True)

class OntolIdentifierResource(Resource):

    @api.expect(parser)
    def get(self):
        """
        Fetches a map from CURIEs/IDs to labels
        """
        args = parser.parse_args()

        return batch_fetch_ids(args.label)
    
    @api.expect(parser)
    def post(self):
        """
        Fetches a map from CURIEs/IDs to labels.
        
        Takes 'label' list argument either as a querystring argument or as a key
        in the POST body when content-type is application/json.
        """
        args = parser.parse_args()

        return batch_fetch_ids(args.label)
