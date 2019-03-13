import logging

from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api

from biolink.error_handlers import RouteNotImplementedException

log = logging.getLogger(__name__)

parser = api.parser()
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

class IdentifierMapper(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, source, target):
        """
        TODO maps a list of identifiers from a source to a target
        """
        args = parser.parse_args()
        raise RouteNotImplementedException()
