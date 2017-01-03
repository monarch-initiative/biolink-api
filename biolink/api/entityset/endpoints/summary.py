import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import compact_association_set, association_results
from biogolr.golr_associations import search_associations, GolrFields

from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('entityset', description='foo bar')

parser = api.parser()


parser.add_argument('subject', action='append', help='Entity id, e.g. NCBIGene:84570, NCBIGene:3630')

@ns.route('/summary/')
class EntitySetSummary(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self):
        """
        Summarize a set of objects
        """
        args = parser.parse_args()

        M=GolrFields()
        results = search_associations(subjects=args.get('subject'),
                                      rows=0,
                                      facet_fields=[M.OBJECT_CLOSURE, M.IS_DEFINED_BY],
                                      facet_limit=-1,
                                      **args)
        print("RESULTS="+str(results))
        obj_count_dict = results['facet_counts'][M.OBJECT_CLOSURE]
        del results['facet_counts'][M.OBJECT_CLOSURE]
        return {'results':obj_count_dict, 'facets': results['facet_counts']}

    

@ns.route('/associations/')
class EntitySetAssociations(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    #@api.marshal_list_with(compact_association_set)
    def get(self):
        """
        Summarize a set of objects
        """
        args = parser.parse_args()

        M=GolrFields()
        #results = search_associations(subjects=args.get('subject'),
        #                              rows=0,
        #                              pivot_subject_object=True,
        #                              facet_fields=[],
        #                              facet_limit=-1,
        #                              **args)
        results = search_associations(subjects=args.get('subject'),
                                      select_fields=[M.SUBJECT, M.RELATION, M.OBJECT],
                                      use_compact_associations=True,
                                      rows=999,
                                      facet_fields=[],
                                      **args)
        return results
    

@ns.route('/ora/')
class EntitySetOverRepresentationAnalysis(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self):
        """
        Over-representation analysis
        """
        args = parser.parse_args()

        M=GolrFields()
        results = search_associations(subjects=args.get('subject'),
                                      rows=0,
                                      facet_fields=[M.OBJECT_CLOSURE, M.IS_DEFINED_BY],
                                      facet_limit=-1,
                                      **args)
        print("RESULTS="+str(results))
        obj_count_dict = results['facet_counts'][M.OBJECT_CLOSURE]
        del results['facet_counts'][M.OBJECT_CLOSURE]
        return {'results':obj_count_dict, 'facets': results['facet_counts']}
    
    

