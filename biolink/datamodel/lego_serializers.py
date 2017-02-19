from flask_restplus import fields
from biolink.api.restplus import api

abstract_property_value = api.model('AbstractPropertyValue', {
    'val': fields.String(readOnly=True, description='value part'),
    'pred': fields.String(readOnly=True, description='predicate (attribute) part'),
    'xrefs': fields.List(fields.String, description='Xrefs provenance for property-value'),
})

annotatable = api.model('Annotatable', {
})

model = api.model('Model', {
    'id': fields.String(description='unique ID/CURIE/URI'),
    'title': fields.String(description='textual description'),
    'state': fields.String(description='production or development'),
    'contributors': fields.List(fields.String(), description='list of IRIs of contributors'),
})

type_reference = api.model('TypeReference', {
    'id': fields.String(description='unique ID/CURIE/URI'),
    'label': fields.String(description='textual description'),
})

instance = api.model('Instance', {
    'id': fields.String(description='unique ID/CURIE/URI'),
    'types': fields.List(fields.Nested(type_reference), description='class assertions'),
})

molecular_instance = api.inherits('MolecularInstance', instance, {
})

# TODO - recursive holding
location_instance = api.inherits('LocationInstance', instance, {
})

biological_process_instance = api.inherits('BiologicalProcessInstance', instance, {
})

activity_instance = api.inherits('ActivityInstance', instance, {
    'enabled_by': fields.Nested(molecular_instance, description='gene or gene product or complex that carries out the activity'),
    'occurs_in': fields.List(fields.Nested(molecular_instance, description='component cell or tissue where the activity is carried out')),
    'part_of': fields.List(fields.Nested(molecular_instance, description='component cell or tissue where the activity is carried out')),
})

