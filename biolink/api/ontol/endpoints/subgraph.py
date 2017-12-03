import logging

from flask import request
from flask_restplus import Resource
from biolink.api.restplus import api
from biolink.ontology.ontology_manager import get_ontology
from ontobio.ontol_factory import OntologyFactory
from ontobio.io.ontol_renderers import OboJsonGraphRenderer
from ontobio.config import get_config
import networkx as nx

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('ontol', description='extract a subgraph from an ontology')

parser = api.parser()
parser.add_argument('cnode', action='append', help='Additional classes')
parser.add_argument('include_meta', type=bool, help='Additional classes')
parser.add_argument('relation', action='append', default=['subClassOf', 'BFO:0000050'], help='Additional classes')

@ns.route('/subgraph/<ontology>/<node>')
@api.doc(params={'ontology': 'ontology id, e.g. go, uberon, mp, hp)'})
@api.doc(params={'node': 'class id. E.g. UBERON:0002102'})
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

        factory = OntologyFactory()
        ont = get_ontology(ontology)
        #subont = ont.subontology([id], relations=args.relations)
        relations = args.relation
        print("Traversing: {} using {}".format(qnodes,relations))
        nodes = ont.traverse_nodes(qnodes,
                                   up=True,
                                   down=False,
                                   relations=relations)

        subont = ont.subontology(nodes, relations=relations)
        
        ojr = OboJsonGraphRenderer(include_meta=args.include_meta)
        json_obj = ojr.to_json(subont)
        # TODO: remove this next release of ontobio
        if not args.include_meta:
            for g in json_obj['graphs']:
                for n in g['nodes']:
                    n['meta']={}
        return json_obj


@ns.route('/testme/<ontology>')
class TestMe(Resource):

    @api.expect(parser)
    def get(self, ontology):
        """
        TEST
        """

        ont = get_ontology(ontology)
        return {'z': 'foo',
                'nodes': len(ont.nodes())}
    

    
    
from flask import g
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        logging.info("INITIAL SETUP")
        db = g._database = 10
    return db
