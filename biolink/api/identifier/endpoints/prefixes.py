import logging

from flask import request
from flask_restplus import Resource
from biolink.util.curie_util import get_prefixes, expand_uri, contract_uri
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('identifier/prefixes', description='identifier prefixies')

parser = api.parser()

@ns.route('/')
class PrefixCollection(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of prefixes
        """
        return get_prefixes()

@ns.route('/expand/<id>')
@api.doc(params={'id': 'ID of entity to be contracted to URI, e.g "MGI:1"'})
class PrefixCollection(Resource):

    @api.expect(parser)
    def get(self, id):
        """
        Returns expanded URI
        """
        return expand_uri(id)

@ns.route('/contract/<path:uri>')
@api.doc(params={'uri': 'URI of entity to be contracted to identifier/CURIE, e.g "http://www.informatics.jax.org/accession/MGI:1"'})
class PrefixCollection(Resource):

    @api.expect(parser)
    def get(self, uri):
        """
        Returns contracted URI
        """
        print(str(uri))
        return contract_uri(uri)
    

    
    

