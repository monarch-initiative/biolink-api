import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from biolink.util.golr_associations import get_associations
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('link/search', description='Find links')

parser = api.parser()
parser.add_argument('subject', help='SUBJECT id, e.g. NCBIGene:84570. Includes inferred by default')
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('object', help='OBJECT id, e.g. HP:0011927. Includes inferred by default')
parser.add_argument('graphize', type=bool, help='If set, includes graph object in response')


@ns.route('/')
@ns.route('/<subject_category>/')
@ns.route('/<subject_category>/<object_category>/')
@api.doc(params={'subject_category': 'CATEGORY of entity at link SUBJECT (source), e.g. gene, disease, genotype'})
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
class AssociationCollection(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, subject_category='gene', object_category='gene'):
        """
        Returns list of associations
        """
        args = parser.parse_args()

        return get_associations(subject_category, object_category, args)
    
    

