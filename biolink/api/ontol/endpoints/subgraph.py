import logging

from flask import request
from flask_restplus import Resource
#from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from obographs.sparql2ontology import *
from obographs.graph_io import OboJsonGraphRenderer
from obographs.graph_manager import retrieve_filtered_graph

# TODO - use separate library
from networkx.algorithms.dag import ancestors, descendants

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('ontol/subgraph', description='extract a subgraph from an ontology')

parser = api.parser()
parser.add_argument('cnode', action='append', help='Additional classes')
parser.add_argument('relation', action='append', default=['subClassOf', 'BFO:0000050'], help='Additional classes')

def get_digraph_wrap(ont, properties=['subClassOf']):
    return g

@ns.route('/<ontology>/<node>')
#@api.doc(params={'ontology': 'ontology id, e.g. go, uberon, mp, hp)'})
@api.doc(params={'node': 'class id. E.g. UBERON:0002102'})
class ExtractOntologySubgraphResource(Resource):

    @api.expect(parser)
    def get(self, ontology, node):
        """
        Extract a subgraph from an ontology
        """
        args = parser.parse_args()

        ids = [node]
        if args.cnode is not None:
            ids += args.cnode
            
        g = retrieve_filtered_graph(ontology, predicates=args.relation)
        
        nodes = set()
        for id in ids:
            nodes.update(ancestors(g,id))
            nodes.update(descendants(g,id))
            nodes.add(id)
        subg = g.subgraph(nodes)
        ojr = OboJsonGraphRenderer()
        json_obj = ojr.to_json(subg)
        return json_obj

    

    
    

