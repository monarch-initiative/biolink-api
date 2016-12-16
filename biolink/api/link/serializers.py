from flask_restplus import fields
from biolink.api.restplus import api

# todo: split this into modules
## BBOP/OBO Graphs


node = api.model('Node', {
    'id': fields.String(readOnly=True, description='ID'),
    'lbl': fields.String(readOnly=True, description='RDFS Label')
})

edge = api.model('Edge', {
    'sub': fields.String(readOnly=True, description='Subject Node ID'),
    'pred': fields.String(readOnly=True, description='Predicate (Relation) ID'),
    'obj': fields.String(readOnly=True, description='Subject Node ID'),
})

bbop_graph = api.model('Graph', {
    'nodes': fields.List(fields.Nested(node)),
    'edges': fields.List(fields.Nested(edge)),
})


named_object = api.model('NamedObject', {
    'id': fields.String(readOnly=True, description='ID'),
    'label': fields.String(readOnly=True, description='RDFS Label'),
    'category': fields.String(readOnly=True, description='Type of object')
})


# todo: inherits
taxon = api.model('Taxon', {
    'id': fields.String(readOnly=True, description='ID'),
    'label': fields.String(readOnly=True, description='RDFS Label')
})

bio_object = api.inherit('BioObject', named_object, {
    'taxon': fields.Nested(taxon)
})

# Assoc

association = api.model('Association', {
    'id': fields.Integer(readOnly=True, description='Association ID'),
    'subject': fields.Nested(bio_object),
    'object': fields.Nested(bio_object),
    'evidence_graph': fields.Nested(bbop_graph),
})

association_results = api.model('AssociationResults', {
    'associations': fields.List(fields.Nested(association)),
    'facets': fields.List(fields.String()),
})


