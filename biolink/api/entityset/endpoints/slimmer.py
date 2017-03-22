import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biogolr.golr_associations import map2slim
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bioentityset', description='maps a set of entities to a slim')

parser = api.parser()
parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID (IMPLEMENTED) or subset ID (TODO)')

@ns.route('/slimmer/<category>')
class EntitySetSlimmer(Resource):

    @api.expect(parser)
    def get(self, category):
        """
        Summarize a set of objects
        """
        args = parser.parse_args()

        slim = args.get('slim')
        del args['slim']
        subjects = args.get('subject')
        del args['subject']
        results = map2slim(subjects=subjects,
                           slim=slim,
                           object_category=category,
                           **args)
        return results

    
    

