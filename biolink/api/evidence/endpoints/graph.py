import logging

from flask import request, send_file
from flask_restplus import Resource
from biolink.datamodel.serializers import association, bbop_graph
from ontobio.golr.golr_associations import get_association, search_associations
from biolink.api.restplus import api
from ontobio.obograph_util import convert_json_object
import tempfile
import pysolr
import matplotlib.pyplot as plt
import networkx as nx

from biolink import USER_AGENT

log = logging.getLogger(__name__)

parser = api.parser()
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

@api.doc(params={'id': 'association id, e.g. cfef92b7-bfa3-44c2-a537-579078d2de37'})
class EvidenceGraphObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self, id):
        """
        Returns evidence graph object for a given association.

        Note that every association is assumed to have a unique ID
        """
        args = parser.parse_args()

        ## TODO: restore this next release of OntoBio (0.2.3 or higher)
        ## assoc = get_association(id)
        
        results = search_associations(fq={'id':id}, user_agent=USER_AGENT)
        assoc = results['associations'][0] if len(results['associations']) > 0 else {}
        eg = assoc.get('evidence_graph')
        return [eg]

@api.doc(params={'id': 'association id, e.g. cfef92b7-bfa3-44c2-a537-579078d2de37'})
class EvidenceGraphImage(Resource):

    @api.expect(parser)
    def get(self, id):
        """
        Returns evidence graph as a png
        """
        assoc = get_association(id, user_agent=USER_AGENT)
        eg = {'graphs':[assoc.get('evidence_graph')]}
        digraph = convert_json_object(eg)
        tmp_dir = tempfile._get_default_tempdir()
        graph = digraph['graph']

        # remove nodes connected to nothing
        graph.remove_nodes_from(list(nx.isolates(graph)))

        node_labels = {}
        for node in dict(graph.nodes()).values():
            if node['label'] is not None:
                node_labels[node['id']] = node['label']
            elif node['id'].startswith('MONARCH'):
                node_labels[node['id']] = 'association'
            else:
                node_labels[node['id']] = node['id']

        plt.axis('off')
        plt.figure(figsize=(10, 10))
        nx.draw(graph, with_labels=True, labels=node_labels)
        #edge_labels = nx.get_edge_attributes(graph, 'lbl')
        #nx.draw_networkx_edge_labels(graph, pos=nx.spring_layout(graph),
        #                             edge_labels=edge_labels)

        tmp_file = tmp_dir + '/' + id + '.png'
        plt.savefig(tmp_file)
        return send_file(tmp_file)
