from biolink import USER_AGENT
from biolink.datamodel.serializers import bbop_graph, association_results
from biolink.api.restplus import api

from ontobio.golr.golr_associations import get_association, search_associations
from ontobio.obograph_util import convert_json_object, obograph_to_assoc_results

from flask import request, send_file
from flask_restplus import Resource
import networkx as nx
import logging
import tempfile
import pysolr
#import matplotlib.pyplot as plt


log = logging.getLogger(__name__)

parser = api.parser()


@api.doc(params={'id': 'association id, e.g. 68e686f6-d05b-46b8-ab1f-1da2fff97ada'})
class EvidenceGraphObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self, id):
        """
        Returns evidence graph object for a given association.

        Note that every association is assumed to have a unique ID
        """
        results = search_associations(
            fq={'id': id},
            facet=False,
            select_fields=['evidence_graph'],
            user_agent=USER_AGENT)
        assoc = results['associations'][0] if len(results['associations']) > 0 else {}
        eg = assoc.get('evidence_graph')
        return [eg]


@api.doc(params={'id': 'association id, e.g. 68e686f6-d05b-46b8-ab1f-1da2fff97ada'})
class EvidenceGraphTable(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns evidence as a association_results object given an association.

        Note that every association is assumed to have a unique ID
        """
        results = search_associations(
            fq={'id': id},
            facet=False,
            select_fields=['subject','object','evidence_graph'],
            user_agent=USER_AGENT)
        assoc = results['associations'][0] if len(results['associations']) > 0 else {}
        eg = {'graphs': [assoc.get('evidence_graph')]}
        digraph = convert_json_object(eg, reverse_edges=False)['graph']
        return  obograph_to_assoc_results(digraph)


@api.doc(params={'id': 'association id, e.g. 68e686f6-d05b-46b8-ab1f-1da2fff97ada'})
class EvidenceGraphImage(Resource):

    @api.expect(parser)
    def get(self, id):
        """
        Returns evidence graph as a png

        TODO - requires matplotlib which is hard to install
        """
        args = parser.parse_args()

        assoc = get_association(id, user_agent=USER_AGENT)
        eg = {'graphs':[assoc.get('evidence_graph')]}
        digraph = convert_json_object(eg)
        #fp = tempfile.TemporaryFile()
        nx.draw(digraph)
        fn = '/tmp/'+id+'.png' # TODO
        #plt.savefig(fn)
        return send_file(fn)
