import logging

from flask import request
from flask_restplus import Resource
#from biolink.api.associations.business import create_association, delete_association, update_association
from biolink.api.search.serializers import association
from biolink.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('search/associations', description='Operations related to association search')


@ns.route('/')
class AssociationCollection(Resource):

    @api.marshal_list_with(association)
    def get(self):
        """
        Returns list of associations
        """
        assoc = {'id':1, 'subject': {'id':"x"}}
        associations = [assoc]
        return associations

    

