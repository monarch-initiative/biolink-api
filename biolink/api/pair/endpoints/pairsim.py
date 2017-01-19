import logging

from flask import request
from flask_restplus import Resource
from biogolr.golr_sim import subject_pair_simj
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('pair/sim', description='pairwise similarity between two entities')

parser = api.parser()
parser.add_argument('object_category', help='e.g. disease, phenotype, gene. Two subjects will be compared based on overlap between associations to objects in this category')

@ns.route('/jaccard/<id1>/<id2>/')
@api.doc(params={'id1': 'id, e.g. NCBIGene:10891; ZFIN:ZDB-GENE-980526-166; UniProtKB:Q15465'})
@api.doc(params={'id2': 'id, e.g. NCBIGene:1200; ZFIN:ZDB-GENE-980528-2059; UniProtKB:P12644'})
class PairSimJaccardResource(Resource):

    @api.expect(parser)
    def get(self, id1, id2):
        """
        Get pairwise similarity
        """
        args = parser.parse_args()

        results = subject_pair_simj(id1,
                                    id2,
                                    **args)
        return results
    

    
    

