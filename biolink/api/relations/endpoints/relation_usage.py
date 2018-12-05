import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from ontobio.golr.golr_associations import get_association, search_associations, GolrFields
from biolink import USER_AGENT

log = logging.getLogger(__name__)

M=GolrFields()

parser = api.parser()
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)

class RelationUsageResource(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        All relations used plus count of associations
        """
        args = parser.parse_args()

        return search_associations(
            rows=0,
            facet_fields=[M.RELATION],
            facet_pivot_fields=[M.SUBJECT_CATEGORY, M.OBJECT_CATEGORY, M.RELATION],
            user_agent=USER_AGENT,
            **args
        )

class RelationUsageBetweenResource(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject_category, object_category):
        """
        All relations used plus count of associations
        """
        args = parser.parse_args()

        return search_associations(
            rows=0,
            subject_category=subject_category,
            object_category=object_category,
            facet_fields=[M.RELATION, M.RELATION_LABEL],
            user_agent=USER_AGENT,
            **args
        )

class RelationUsagePivotResource(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Relation usage count for all subj x obj category combinations
        """
        args = parser.parse_args()

        return search_associations(
            rows=0,
            facet_fields=[M.RELATION],
            facet_pivot_fields=[M.SUBJECT_CATEGORY, M.OBJECT_CATEGORY, M.RELATION],
            user_agent=USER_AGENT,
            **args
        )

class RelationUsagePivotLabelResource(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Relation usage count for all subj x obj category combinations, showing label
        """
        args = parser.parse_args()

        return search_associations(
            rows=0,
            facet_fields=[M.RELATION_LABEL],
            facet_pivot_fields=[M.SUBJECT_CATEGORY, M.OBJECT_CATEGORY, M.RELATION_LABEL],
            user_agent=USER_AGENT,
            **args
        )
    
    
    

