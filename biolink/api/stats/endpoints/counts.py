import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biogolr.golr_associations import search_associations
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('stats', description='foo bar')

parser = api.parser()

@ns.route('/thing/<id>')
@ns.route('/thing/<id>/<object_category>')
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
class ThingCountResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id, object_category):

        """
        return the number of annotations to each ontology class in a given category
        """
        args = parser.parse_args()

        results = search_associations(object_category=object_category,
                                      subject=id,
                                      rows=0,
                                      **args)
        facet_count_dict = results['facet_counts']
        # TODO: map this for GO golr fields
        return facet_count_dict['object_closure']


parser.add_argument('eid', action='append', help='Entity id, e.g. NCBIGene:84570, NCBIGene:3630')

@ns.route('/bioset/summary/')
class ThingSummary(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self):
        """
        Summarize a set of objects
        """
        args = parser.parse_args()

        results = search_associations(subjects=args.get('eid'),
                                      rows=0,
                                      facet_fields=['object'],
                                      facet_limt=-1,
                                      **args)
        facet_count_dict = results['facet_counts']
        # TODO: map this for GO golr fields
        return facet_count_dict
    

    
    

