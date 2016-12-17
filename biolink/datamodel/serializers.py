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


# Bio Objects

sequence_feature = api.inherit('SequenceFeature', bio_object, {
})

gene = api.inherit('Gene', sequence_feature, {
})

gene_product = api.inherit('GeneProduct', sequence_feature, {
    'genes': fields.List(fields.Nested(gene))
})

transcript = api.inherit('Transcript', sequence_feature, {
    'genes': fields.List(fields.Nested(gene))
})

genotype = api.inherit('Genotype', sequence_feature, {
    'genes': fields.List(fields.Nested(gene))
})

allele = api.inherit('Allele', sequence_feature, {
    'genes': fields.List(fields.Nested(gene))
})

# molecular entities
molecular_complex = api.inherit('MolecularComplex', bio_object, {
    'genes': fields.List(fields.Nested(gene))
})

drug = api.inherit('Drug', bio_object, {
    'target_associations': fields.List(fields.Nested(association))
})

