import logging

from flask import request
from flask_restplus import Resource
#from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from obographs.sparql2ontology import *
from obographs.graph_io import OboJsonGraphRenderer

# TODO - use separate library
from networkx.algorithms.dag import ancestors, descendants

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('ontol/subgraph', description='extract a subgraph from an ontology')

parser = api.parser()
parser.add_argument('cnode', action='append', help='Additional classes')

def get_digraph_wrap(ont, properties=['subClassOf']):
    return g

@ns.route('/<ontol>/<node>')
class ExtractOntologySubgraphResource(Resource):

    @api.expect(parser)
    def get(self, ontol, node):
        """
        Extract a subgraph from an ontology
        """
        args = parser.parse_args()

        ids = [node]
        if args.cnode is not None:
            ids += args.cnode
        # TODO: args
        g = get_digraph(ontol, ['subClassOf', 'BFO:0000050'], True)
        
        nodes = set()
        for id in ids:
            nodes.update(ancestors(g,id))
            nodes.update(descendants(g,id))
            nodes.add(id)
        subg = g.subgraph(nodes)
        ojr = OboJsonGraphRenderer()
        json_obj = ojr.to_json(subg)
        return json_obj

    

    
    

