import logging

from flask import request, send_file
from flask_restplus import Resource
from biolink.datamodel.serializers import association, bbop_graph
from ontobio.golr.golr_associations import get_association, search_associations
from biolink.api.restplus import api
from ontobio.obograph_util import convert_json_object
import tempfile
import pysolr
#import matplotlib.pyplot as plt
import networkx as nx

from biolink import USER_AGENT

log = logging.getLogger(__name__)

parser = api.parser()
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

@api.doc(params={'id': 'association id, e.g. cfef92b7-bfa3-44c2-a537-579078d2de37'})
class EvidenceGraphObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(bbop_graph)
    def get(self,id):
        """
        Returns evidence graph object for a given association.

        Note that every association is assumed to have a unique ID
        """
        args = parser.parse_args()

        ## TODO: restore this next release of OntoBio (0.2.3 or higher)
        ## assoc = get_association(id)
        
        results = search_associations(fq={'id':id}, user_agent=USER_AGENT)
        assoc = results['associations'][0]
        eg = assoc.get('evidence_graph')
        return [eg]

@api.doc(params={'id': 'association id, e.g. cfef92b7-bfa3-44c2-a537-579078d2de37'})
class EvidenceGraphImage(Resource):

    @api.expect(parser)
    def get(self,id):
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
        plt.savefig(fn)
        return send_file(fn)
        
    


    
    

