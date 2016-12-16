from flask_restplus import fields
from biolink.api.restplus import api

named_object = api.model('NamedObject', {
    'id': fields.String(readOnly=True, description='ID'),
    'label': fields.String(readOnly=True, description='RDFS Label')
    
})
    
association = api.model('Association', {
    'id': fields.Integer(readOnly=True, description='Association ID'),
    'subject': fields.Nested(named_object),
    'title': fields.String(required=True, description='Article title'),
    'body': fields.String(required=True, description='Article content'),
    'pub_date': fields.DateTime,
    'category_id': fields.Integer(attribute='category.id'),
    'category': fields.String(attribute='category.id'),
})

