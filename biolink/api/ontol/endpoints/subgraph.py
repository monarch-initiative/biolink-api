import logging

from flask import request
from flask_restplus import Resource
from biolink.api.restplus import api
from obographs.ontol_factory import OntologyFactory
from obographs.graph_io import OboJsonGraphRenderer
import networkx as nx

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('ontol/subgraph', description='extract a subgraph from an ontology')

parser = api.parser()
parser.add_argument('cnode', action='append', help='Additional classes')
parser.add_argument('relation', action='append', default=['subClassOf', 'BFO:0000050'], help='Additional classes')


@ns.route('/<ontology>/<node>')
@api.doc(params={'ontology': 'ontology id, e.g. go, uberon, mp, hp)'})
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

        factory = OntologyFactory()
        ont = factory.create(ontology)
        g = ont.get_filtered_graph(relations=args.relation)
        
        nodes = set()

        dirn = 'du'
        for id in ids:
            nodes.add(id)
            # NOTE: we use direct networkx methods as we have already extracted
            # the subgraph we want
            if dirn.find("u") > -1:
                nodes.update(nx.ancestors(g, id))
            if dirn.find("d") > -1:
                nodes.update(nx.descendants(g, id))
        subg = g.subgraph(nodes)
        ojr = OboJsonGraphRenderer()
        json_obj = ojr.to_json(subg)
        return json_obj

    

    
    

