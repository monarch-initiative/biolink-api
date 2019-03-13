import logging

from flask_restplus import reqparse
from flask import request
from flask_restplus import Resource
from biolink.api.variation.business import create_variantset, update_variantset, delete_variantset
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from biolink.database.models import VariantSet

from biolink.error_handlers import RouteNotImplementedException

log = logging.getLogger(__name__)

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, choices=[2, 10, 20, 30, 40, 50],
                                  default=10, help='Results per page {error_msg}')

# transient data model

from flask_restplus import fields
variantset = api.model('variant set', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a variant set'),
    'title': fields.String(required=True, description='Article title'),
    'body': fields.String(required=True, description='Article content'),
    'pub_date': fields.DateTime,
    'category_id': fields.Integer(attribute='category.id'),
    'category': fields.String(attribute='category.id'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_variantsets = api.inherit('Page of variant sets', pagination, {
    'items': fields.List(fields.Nested(variantset))
})

class VariantSetsCollection(Resource):

    @api.expect(pagination_arguments)
    @api.marshal_with(page_of_variantsets)
    def get(self):
        """
        Returns list of variant sets.
        """
        args = pagination_arguments.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)

        posts_query = VariantSet.query
        posts_page = posts_query.paginate(page, per_page, error_out=False)

        return posts_page

    @api.expect(variantset)
    def post(self):
        """
        Creates a new variant set.
        """
        create_variantset(request.json)
        return None, 201

@api.response(404, 'VariantSet not found.')
class VariantSetItem(Resource):

    @api.marshal_with(variantset)
    def get(self, id):
        """
        Returns a variant set.
        """
        return VariantSet.query.filter(VariantSet.id == id).one()

    @api.expect(variantset)
    @api.response(204, 'VariantSet successfully updated.')
    def put(self, id):
        """
        Updates a variant set.
        """
        data = request.json
        update_post(id, data)
        return None, 204

    @api.response(204, 'VariantSet successfully deleted.')
    def delete(self, id):
        """
        Deletes variant set.
        """
        delete_post(id)
        return None, 204

class VariantSetsArchiveCollection(Resource):

    @api.expect(pagination_arguments, validate=True)
    @api.marshal_with(page_of_variantsets)
    def get(self, year, month=None, day=None):
        """
        Returns list of variant sets from a specified time period.
        """
        args = pagination_arguments.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)

        start_month = month if month else 1
        end_month = month if month else 12
        start_day = day if day else 1
        end_day = day + 1 if day else 31
        start_date = '{0:04d}-{1:02d}-{2:02d}'.format(year, start_month, start_day)
        end_date = '{0:04d}-{1:02d}-{2:02d}'.format(year, end_month, end_day)
        posts_query = VariantSet.query.filter(VariantSet.pub_date >= start_date).filter(VariantSet.pub_date <= end_date)

        posts_page = posts_query.paginate(page, per_page, error_out=False)

        return posts_page

class VariantAnalyze(Resource):

    #@api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, term):
        """
        Returns list of matches
        """
        args = parser.parse_args()
        raise RouteNotImplementedException()
    
