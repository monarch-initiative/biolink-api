import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.api.restplus import api
from biolink.ontology.ontology_manager import get_ontology
from ontobio.io.ontol_renderers import OboJsonGraphRenderer
from ontobio.config import get_config
import networkx as nx

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('ontol', description='extract a subgraph from an ontology')

parser = api.parser()
parser.add_argument('cnode', action='append', help='Additional classes')
parser.add_argument('include_ancestors', type=inputs.boolean, default=True, help='Include Ancestors')
parser.add_argument('include_descendants', type=inputs.boolean, help='Include Descendants')
parser.add_argument('relation', action='append', default=['subClassOf', 'BFO:0000050'], help='Additional classes')
parser.add_argument('include_meta', type=inputs.boolean, default=False, help='Include metadata in response')

@ns.route('/subgraph/<ontology>/<node>')
@api.doc(params={'ontology': 'ontology ID, e.g. go, uberon, mp, hp'})
@api.doc(params={'node': 'class ID, e.g. HP:0001288'})
class ExtractOntologySubgraphResource(Resource):

    @api.expect(parser)
    def get(self, ontology, node):
        """
        Extract a subgraph from an ontology
        """
        args = parser.parse_args()
        qnodes = [node]
        if args.cnode is not None:
            qnodes += args.cnode

        ont = get_ontology(ontology)
        relations = args.relation
        print("Traversing: {} using {}".format(qnodes,relations))
        nodes = ont.traverse_nodes(qnodes,
                                   up=args.include_ancestors,
                                   down=args.include_descendants,
                                   relations=relations)

        subont = ont.subontology(nodes, relations=relations)
        ojr = OboJsonGraphRenderer()
        json_obj = ojr.to_json(subont, include_meta=args.include_meta)

        return json_obj


# @ns.route('/testme/<ontology>')
# class TestMe(Resource):

#     @api.expect(parser)
#     def get(self, ontology):
#         """
#         TEST
#         """

#         ont = get_ontology(ontology)
#         return {'z': 'foo',
#                 'nodes': len(ont.nodes())}
    

    
    
from flask import g
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        logging.info("INITIAL SETUP")
        db = g._database = 10
    return db
