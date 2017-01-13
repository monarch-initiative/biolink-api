import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from biogolr.golr_associations import get_association, search_associations, GolrFields
import pysolr

log = logging.getLogger(__name__)

M=GolrFields()

ns = api.namespace('relation/usage', description='Usage of different relationship types')

parser = api.parser()
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)


@ns.route('/')
class AssociationSearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        All relations used plus count of associations
        """
        args = parser.parse_args()

        return search_associations(rows=0,
                                   facet_fields=[M.RELATION],
                                   facet_pivot_fields=[M.SUBJECT_CATEGORY, M.OBJECT_CATEGORY, M.RELATION],
                                   **args)

@ns.route('/pivot/')
class AssociationSearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Relation usage count for all subj x obj category combinations
        """
        args = parser.parse_args()

        return search_associations(rows=0,
                                   facet_fields=[M.RELATION],
                                   facet_pivot_fields=[M.SUBJECT_CATEGORY, M.OBJECT_CATEGORY, M.RELATION],
                                   **args)
    
    
@ns.route('/pivot/label')
class AssociationSearch(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Relation usage count for all subj x obj category combinations, showing label
        """
        args = parser.parse_args()

        return search_associations(rows=0,
                                   facet_fields=[M.RELATION_LABEL],
                                   facet_pivot_fields=[M.SUBJECT_CATEGORY, M.OBJECT_CATEGORY, M.RELATION_LABEL],
                                   **args)
    
    
    

