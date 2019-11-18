import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from ontobio.golr.golr_associations import get_association, search_associations

from biolink import USER_AGENT

log = logging.getLogger(__name__)

core_parser = api.parser()
core_parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
core_parser.add_argument('start', type=int, required=False, help='beginning row')
core_parser.add_argument('evidence', help='Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default) or a specific publication or other supporting object, e.g. ZFIN:ZDB-PUB-060503-2')
core_parser.add_argument('unselect_evidence', type=inputs.boolean, default=False, help='If true, excludes evidence objects in response')
core_parser.add_argument('exclude_automatic_assertions', type=inputs.boolean, default=False, help='If true, excludes associations that involve IEAs (ECO:0000501)')
core_parser.add_argument('use_compact_associations', type=inputs.boolean, default=False, help='If true, returns results in compact associations format')

@api.doc(params={'subject': 'Return associations emanating from this node, e.g. NCBIGene:84570, ZFIN:ZDB-GENE-050417-357 (If ID is from an ontology then results would include inferred associations, by default)'})
class AssociationsFrom(Resource):

    parser = core_parser.copy()
    parser.add_argument('object_taxon', help='Object taxon ID, e.g. NCBITaxon:10090 (Includes inferred associations, by default)')
    parser.add_argument('relation', help='Filter by relation CURIE, e.g. RO:0002200 (has_phenotype), RO:0002607 (is marker for), RO:HOM0000017 (orthologous to), etc.')

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject):
        """
        Returns list of matching associations starting from a given subject (source)
        """
        args = self.parser.parse_args()
        return search_associations(subject=subject, user_agent=USER_AGENT, **args)

@api.doc(params={'object': 'Return associations pointing to this node, e.g. specifying MP:0013765 will return all genes, variants, strains, etc. annotated with this term. Can also be a biological entity such as a gene'})
class AssociationsTo(Resource):

    parser = core_parser.copy()
    parser.add_argument('subject_taxon', help='Subject taxon ID, e.g. NCBITaxon:9606 (Includes inferred associations, by default)')
    parser.add_argument('relation', help='Filter by relation CURIE, e.g. RO:0002200 (has_phenotype), RO:0002607 (is marker for), RO:HOM0000017 (orthologous to), etc.')

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, object):
        """
        Returns list of matching associations pointing to a given object (target)
        """
        args = self.parser.parse_args()
        return search_associations(object=object, user_agent=USER_AGENT, **args)

@api.doc(params={'subject': 'Return associations emanating from this node, e.g. MGI:1342287 (If ID is from an ontology then results would include inferred associations, by default)'})
@api.doc(params={'object': 'Return associations pointing to this node, e.g. MP:0013765. Can also be a biological entity such as a gene'})
class AssociationsBetween(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, subject, object):
        """
        Returns associations connecting two entities

        Given two entities (e.g. a particular gene and a particular disease), if these two entities
        are connected (directly or indirectly), then return the association objects describing
        the connection.
        
        """
        args = core_parser.parse_args()
        return search_associations(subject=subject, object=object, user_agent=USER_AGENT, **args)

@api.doc(params={'association_type': 'Association type, eg gene_phenotype'})
class AssociationBySubjectAndAssocType(Resource):

    parser = core_parser.copy()
    parser.add_argument('subject', help='Subject CURIE')
    parser.add_argument('object', help='Object CURIE')

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, association_type):
        """
        Returns list of matching associations of a given type
        """
        args = self.parser.parse_args()
        return search_associations(
            association_type=association_type,
            sort="source_count desc",
            user_agent=USER_AGENT,
            **args
        )
