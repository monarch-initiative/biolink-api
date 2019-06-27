import logging

from flask_restplus import Resource
from biolink.datamodel.serializers import compact_association_set, association_results
from ontobio.golr.golr_associations import search_associations, GolrFields

from biolink.api.restplus import api
from biolink import USER_AGENT
from biolink.error_handlers import RouteNotImplementedException

MAX_ROWS=10000

log = logging.getLogger(__name__)

parser = api.parser()

parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('background', action='append', help='Entity ids in background set, e.g. NCBIGene:84570, NCBIGene:3630; used in over-representation tests')
parser.add_argument('object_category', help='E.g. phenotype, function')
parser.add_argument('object_slim', help='Slim or subset to which the descriptors are to be mapped, NOT IMPLEMENTED')

class EntitySetSummary(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self):
        """
        Summary statistics for objects associated
        """
        args = parser.parse_args()
        subjects = args.get('subject')
        del args['subject']
        M=GolrFields()
        results = search_associations(
            subjects=subjects,
            rows=0,
            facet_fields=[M.OBJECT_CLOSURE, M.IS_DEFINED_BY],
            facet_limit=-1,
            user_agent=USER_AGENT,
            **args
        )
        print("RESULTS="+str(results))
        obj_count_dict = results['facet_counts'][M.OBJECT_CLOSURE]
        del results['facet_counts'][M.OBJECT_CLOSURE]
        return {'results':obj_count_dict, 'facets': results['facet_counts']}

class EntitySetAssociations(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Returns compact associations for a given input set
        """
        args = parser.parse_args()

        M=GolrFields()
        subjects = args.get('subject')
        del args['subject']
        results = search_associations(
            subjects=subjects,
            select_fields=[M.SUBJECT, M.RELATION, M.OBJECT],
            use_compact_associations=True,
            rows=MAX_ROWS,
            facet_fields=[],
            user_agent=USER_AGENT,
            **args
        )
        return results

#@ns.route('/DEPRECATEDhomologs/')
#class EntitySetHomologsDEPRECATED(Resource):
#
#    @api.expect(parser)
#    @api.marshal_list_with(association_results)
#    #@api.marshal_list_with(compact_association_set)
#    def get(self):
#        """
#        Returns homology associations for a given input set of genes
#        """
#        args = parser.parse_args()
#
#        M=GolrFields()
#        rel = 'RO:0002434'  # TODO; allow other types
#        results = search_associations(subjects=args.get('subject'),
#                                      select_fields=[M.SUBJECT, M.RELATION, M.OBJECT],
#                                      use_compact_associations=True,
#                                      relation=rel,
#                                      rows=MAX_ROWS,
#                                      facet_fields=[],
#                                      **args)
#        return results
    

class EntitySetGraphResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self):
        """
        TODO Graph object spanning all entities
        """
        args = parser.parse_args()

        raise RouteNotImplementedException()
