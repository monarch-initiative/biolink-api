from flask_restplus import fields
from biolink.api.restplus import api

abstract_property_value = api.model('AbstractPropertyValue', {
    'val': fields.String(readOnly=True, description='value part'),
    'pred': fields.String(readOnly=True, description='predicate (attribute) part'),
    'xrefs': fields.List(fields.String, description='Xrefs provenance for property-value'),
})

synonym_property_value = api.inherit('SynonymPropertyValue', abstract_property_value, {
})

xref_property_value = api.inherit('SynonymPropertyValue', abstract_property_value, {
})

definition_property_value = api.inherit('DefinitionPropertyValue', abstract_property_value, {
})

basic_property_value = api.inherit('DefinitionPropertyValue', abstract_property_value, {
})

meta = api.model('Meta', {
    'definition': fields.Nested(definition_property_value, description='definition plus source'),
    'comments': fields.List(fields.String(readOnly=True), description='comments'),
    'subsets': fields.List(fields.String(readOnly=True), description='subsets (slims)'),
    'xrefs': fields.List(fields.Nested(xref_property_value), description='xrefs plus source'),
    'synonyms': fields.List(fields.Nested(synonym_property_value), description='synonyms plus scope, type and source'),
    'basic_property_values': fields.List(fields.Nested(basic_property_value), description='synonyms plus scope, type and source'),
})


node = api.model('Node', {
    'id': fields.String(readOnly=True, description='ID or CURIE'),
    'lbl': fields.String(readOnly=True, description='human readable label, maps to rdfs:label')
})

edge = api.model('Edge', {
    'sub': fields.String(readOnly=True, description='Subject (source) Node ID'),
    'pred': fields.String(readOnly=True, description='Predicate (relation) ID'),
    'obj': fields.String(readOnly=True, description='Object (target) Node ID'),
})

graph = api.model('Graph', {
    'nodes': fields.List(fields.Nested(node), description='All nodes in graph'),
    'edges': fields.List(fields.Nested(edge), description='All edges in graph'),
})

graph_document = api.model('GraphDocument', {
    'graphs': fields.List(fields.Nested(graph), description='all graphs'),
})
