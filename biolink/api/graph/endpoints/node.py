import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, bbop_graph
from scigraph.scigraph_util import SciGraph
from biolink.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('graph/node', description='Graph nodes')

parser = api.parser()
sg = SciGraph()

@ns.route('/<id>')
@api.doc(params={'id': 'CURIE e.g. HP:0000465'})
class SearchEntities(Resource):

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self, id):
        """
        Returns list of matches
        """
        args = parser.parse_args()
        
        return sg.graph(id)

