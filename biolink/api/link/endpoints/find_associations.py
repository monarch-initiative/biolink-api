import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from biogolr.golr_associations import get_association, search_associations, GolrFields
import pysolr

log = logging.getLogger(__name__)

M=GolrFields()

ns = api.namespace('association', description='Associations between entities or entity and descriptors')

parser = api.parser()
parser.add_argument('subject', help='SUBJECT id, e.g. NCBIGene:84570, ZFIN:ZDB-GENE-050417-357. Includes inferred by default')
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('object', help='OBJECT id, e.g. HP:0011927. Includes inferred by default')
parser.add_argument('objects', append=True,help='list of OBJECT id, e.g. HP:0011927. Includes inferred by default')
parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)
parser.add_argument('graphize', type=bool, help='If set, includes graph object in response')
parser.add_argument('fl_excludes_evidence', type=bool, help='If set, excludes evidence objects in response')
parser.add_argument('page', type=int, required=False, default=1, help='Page number')
parser.add_argument('rows', type=int, required=False, default=10, help='number of rows')
parser.add_argument('map_identifiers', help='Prefix to map all IDs to. E.g. NCBIGene')

@ns.route('/<id>')
class AssociationObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self,id):
        """
        Returns the association with a given identifier.

        An association connects, at a minimum, two things, designated subject and object,
        via some relationship. Associations also include evidence, provenance etc.
        """
        args = parser.parse_args()

        return get_association(id)


@ns.route('/find/')
class AssociationSearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Generalized search over complete corpus of associations
        """
        args = parser.parse_args()

        return search_associations(**args)

@ns.route('/find/<subject_category>/')
@ns.route('/find/<subject_category>/<object_category>/')
@api.doc(params={'subject_category': 'CATEGORY of entity at link SUBJECT (source), e.g. gene, disease, genotype'})
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
class AssociationSearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject_category='gene', object_category='gene'):
        """
        Returns list of matching associations
        """
        args = parser.parse_args()

        return search_associations(subject_category, object_category, **args)

    
    
    

