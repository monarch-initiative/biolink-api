import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from ontobio.golr.golr_associations import get_association, search_associations, GolrFields

from biolink import USER_AGENT

log = logging.getLogger(__name__)

M=GolrFields()

core_parser = api.parser()
core_parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
core_parser.add_argument('start', type=int, required=False, help='beginning row')
core_parser.add_argument('evidence', help='Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default) or a specific publication or other supporting object, e.g. ZFIN:ZDB-PUB-060503-2')
core_parser.add_argument('unselect_evidence', type=inputs.boolean, default=False, help='If true, excludes evidence objects in response')
core_parser.add_argument('exclude_automatic_assertions', type=inputs.boolean, default=False, help='If true, excludes associations that involve IEAs (ECO:0000501)')
core_parser.add_argument('use_compact_associations', type=inputs.boolean, default=False, help='If true, returns results in compact associations format')


@api.doc(params={'id': 'identifier for an association, e.g. f5ba436c-f851-41b3-9d9d-bb2b5fc879d4'}, required=True)
class AssociationObject(Resource):

    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns the association with a given identifier.

        An association connects, at a minimum, two things, designated subject and object,
        via some relationship. Associations also include evidence, provenance etc.
        """
        return search_associations(id=id, user_agent=USER_AGENT)

@api.doc(params={'subject_category': 'Category of entity at link Subject (source), e.g. gene, disease, phenotype'}, required=True)
class AssociationBySubjectCategorySearch(Resource):

    parser = core_parser.copy()
    parser.add_argument('subject_taxon', help='Subject taxon ID, e.g. NCBITaxon:9606 (Includes inferred associations, by default)')
    parser.add_argument('object_taxon', help='Object taxon ID, e.g. NCBITaxon:10090 (Includes inferred associations, by default)')
    parser.add_argument('relation', help='Filter by relation CURIE, e.g. RO:0002200 (has_phenotype), RO:0002607 (is marker for), RO:HOM0000017 (orthologous to), etc.')

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject_category):
        """
        Returns list of matching associations for a given subject category.
        """
        args = self.parser.parse_args()
        return search_associations(subject_category=subject_category, user_agent=USER_AGENT, **args)

@api.doc(params={'subject_category': 'Category of entity at link Subject (source), e.g. gene, disease, phenotype'})
@api.doc(params={'object_category': 'Category of entity at link Object (target), e.g. gene, disease, phenotype'})
class AssociationBySubjectAndObjectCategorySearch(Resource):

    parser = core_parser.copy()
    parser.add_argument('subject', help='Subject CURIE')
    parser.add_argument('object', help='Object CURIE')
    parser.add_argument('subject_taxon', help='Subject taxon ID, e.g. NCBITaxon:9606 (Includes inferred associations, by default)')
    parser.add_argument('object_taxon', help='Object taxon ID, e.g. NCBITaxon:10090 (Includes inferred associations, by default)')
    parser.add_argument('relation', help='Filter by relation CURIE, e.g. RO:0002200 (has_phenotype), RO:0002607 (is marker for), RO:HOM0000017 (orthologous to), etc.')

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject_category, object_category):
        """
        Returns list of matching associations between a given subject and object category
        """
        args = self.parser.parse_args()
        return search_associations(
            subject_category=subject_category,
            object_category=object_category,
            user_agent=USER_AGENT,
            **args
        )
