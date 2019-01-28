import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from ontobio.golr.golr_associations import get_association, search_associations, GolrFields

from biolink import USER_AGENT

log = logging.getLogger(__name__)

M=GolrFields()

parser = api.parser()
parser.add_argument('subject', help='Return associations emanating from this node, e.g. NCBIGene:84570, ZFIN:ZDB-GENE-050417-357 (If ID is from an ontology then results would include inferred associations, by default)')
parser.add_argument('subject_taxon', help='Subject taxon ID, e.g. NCBITaxon:9606 (Includes inferred associations, by default)')
parser.add_argument('object', help='Return associations pointing to this node, e.g. HP:0011927 (If ID is from an ontology then results would include inferred associations, by default)')
parser.add_argument('relation', help='Filter by relation CURIE, e.g. RO:0002200 (has_phenotype), RO:0002607 (is marker for), RO:HOM0000017 (orthologous to), etc.')
parser.add_argument('evidence', help='Object ID, e.g. ECO:0000501 (for IEA; Includes inferred associations, by default), a specific publication or other supporting object, e.g. ZFIN:ZDB-PUB-060503-2')
parser.add_argument('graphize', type=inputs.boolean, default=False, help='If true, includes graph object in response')
parser.add_argument('unselect_evidence', type=inputs.boolean, default=False, help='If true, excludes evidence objects in response')
parser.add_argument('start', type=int, required=False, default=0, help='beginning row')
parser.add_argument('rows', type=int, required=False, default=10, help='number of rows')
parser.add_argument('map_identifiers', help='Prefix to map all IDs to, e.g. NCBIGene')

@api.doc(params={'id': 'identifier for an association, e.g. f5ba436c-f851-41b3-9d9d-bb2b5fc879d4'}, required=True)
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

        return get_association(id, user_agent=USER_AGENT)

class AssociationSearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Generalized search over complete corpus of associations
        """
        args = parser.parse_args()

        return search_associations(user_agent=USER_AGENT, **args)

@api.doc(params={'subject_category': 'Category of entity at link Subject (source), e.g. gene, disease, phenotype'}, required=True)
class AssociationBySubjectCategorySearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject_category='gene'):
        """
        Returns list of matching associations for a given Subject category
        """
        args = parser.parse_args()

        return search_associations(subject_category=subject_category, user_agent=USER_AGENT, **args)

@api.doc(params={'subject_category': 'Category of entity at link Subject (source), e.g. gene, disease, phenotype'})
@api.doc(params={'object_category': 'Category of entity at link Object (target), e.g. gene, disease, phenotype'})
class AssociationBySubjectAndObjectCategorySearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject_category='gene', object_category='gene'):
        """
        Returns list of matching associations between a given Subject and Object category
        """
        args = parser.parse_args()
        return search_associations(
            subject_category=subject_category,
            object_category=object_category,
            user_agent=USER_AGENT,
            **args
        )

