import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from ontobio.sparql.sparql_ontol_utils import batch_fetch_labels
import pysolr

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('id', action='append', help='List of ids')

class OntolLabelerResource(Resource):

    @api.expect(parser)
    def get(self):
        """
        Fetches a map from CURIEs/IDs to labels
        """
        args = parser.parse_args()

        return batch_fetch_labels(args.id)


    
    

