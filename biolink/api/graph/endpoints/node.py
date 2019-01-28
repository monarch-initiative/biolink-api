import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, bbop_graph
from scigraph.scigraph_util import SciGraph
from biolink.api.restplus import api

log = logging.getLogger(__name__)

parser = api.parser()
sg = SciGraph()

@api.doc(params={'id': 'CURIE e.g. HP:0000465'})
class NodeResource(Resource):

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self, id):
        """
        Returns a graph node.

        A node is an abstract representation of some kind of entity. The entity may be a physical thing such as a patient,
        a molecular entity such as a gene or protein, or a conceptual entity such as a class from an ontology.
        """
        args = parser.parse_args()
        
        return sg.graph(id)

@api.doc(params={'id': 'CURIE e.g. HP:0000465'})
class EdgeResource(Resource):

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self, id):
        """
        Returns edges emanating from a node. 

        """
        args = parser.parse_args()
        
        return sg.graph(id)
    
