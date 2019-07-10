import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association, bbop_graph, bio_object
from biolink.error_handlers import NoResultFoundException
from scigraph.scigraph_util import SciGraph
from scigraph.model.BBOPGraph import BBOPGraph
from biolink.api.restplus import api
from biolink.settings import get_biolink_config

log = logging.getLogger(__name__)

sg = SciGraph(get_biolink_config()['scigraph_data']['url'])

@api.doc(params={'id': 'CURIE e.g. HP:0000465'})
class NodeResource(Resource):

    @api.marshal_list_with(bio_object)
    def get(self, id):
        """
        Returns a graph node.

        A node is an abstract representation of some kind of entity. The entity may be a physical thing such as a patient,
        a molecular entity such as a gene or protein, or a conceptual entity such as a class from an ontology.
        """
        graph = sg.bioobject(id)
        return graph


@api.doc(params={'id': 'CURIE e.g. HP:0000465'})
class EdgeResource(Resource):

    parser = api.parser()
    parser.add_argument('depth', type=int, help='How far to traverse for neighbors', default=1)
    parser.add_argument('direction', choices=['INCOMING', 'OUTGOING', 'BOTH'], help='Which direction to traverse (used only if relationship_type is defined)', default='BOTH')
    parser.add_argument('relationship_type', action='append', help='Relationship type to traverse')
    parser.add_argument('entail', type=inputs.boolean, help='Include sub-properties and equivalent properties', default=False)

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self, id):
        """
        Returns edges emanating from a given node.

        """
        args = self.parser.parse_args()
        response = sg.get_response("dynamic/cliqueLeader", q=id, format="json", depth=1)
        nodes = response.json()['nodes']
        if not nodes:
            raise NoResultFoundException('SciGraph dynamic/cliqueLeader yields no result for {}'.format(id))

        clique_leader = nodes[0]['id']
        final_graph = BBOPGraph({'nodes': [], 'edges': []})
        if args.relationship_type:
            for relationship in args.relationship_type:
                graph = sg.neighbors(
                    id=clique_leader,
                    relationshipType=relationship,
                    direction=args.direction,
                    depth=args.depth,
                    entail=args.entail
                )
                final_graph.merge(graph)

        else:
            graph = sg.neighbors(
                id=clique_leader,
                depth=args.depth,
                entail=args.entail
            )
            final_graph.merge(graph)

        return final_graph.as_dict()
