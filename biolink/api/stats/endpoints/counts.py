import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('stats/counts', description='foo bar')

parser = api.parser()

@ns.route('/<id>')
@ns.route('/<id>/<object_category>')
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
class Foo(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id, object_category):
        """
        Given an entity ID (e.g. a gene ID), return the number of annotations
        to each ontology class in a given category
        """
        args = parser.parse_args()

        results = search_associations(object_category=object_category,
                                      subject=id,
                                      rows=0,
                                      **args)
        facet_count_dict = results['facet_counts']
        # TODO: map this for GO golr fields
        return facet_count_dict['object_closure']


    
    

