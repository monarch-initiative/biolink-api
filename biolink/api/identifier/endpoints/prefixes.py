import logging

from flask import request
from flask_restplus import Resource
from prefixcommons.curie_util import get_prefixes, expand_uri, contract_uri
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

parser = api.parser()

class PrefixCollection(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of prefixes
        """
        return get_prefixes()

@api.doc(params={'id': 'ID of entity to be contracted to URI, e.g "MGI:1"'})
class PrefixExpand(Resource):

    @api.expect(parser)
    def get(self, id):
        """
        Returns expanded URI
        """
        return expand_uri(id)

@api.doc(params={'uri': 'URI of entity to be contracted to identifier/CURIE, e.g "http://www.informatics.jax.org/accession/MGI:1"'})
class PrefixContract(Resource):

    @api.expect(parser)
    def get(self, uri):
        """
        Returns contracted URI
        """
        return contract_uri(uri)
    

    
    

