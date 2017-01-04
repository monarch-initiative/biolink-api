from flask_restplus import fields
from biolink.api.restplus import api


# todo: split this into modules

# Solr

search_result = api.model('SearchResult', {
    'numFound': fields.Integer(description='total number of associations matching query'),
    'start': fields.Integer(description='Cursor position'),
    'facet_counts': fields.Raw(description='Mapping between field names and association counts')
    })

## BBOP/OBO Graphs


node = api.model('Node', {
    'id': fields.String(readOnly=True, description='ID or CURIE'),
    'lbl': fields.String(readOnly=True, description='human readable label, maps to rdfs:label')
})

edge = api.model('Edge', {
    'sub': fields.String(readOnly=True, description='Subject (source) Node ID'),
    'pred': fields.String(readOnly=True, description='Predicate (relation) ID'),
    'obj': fields.String(readOnly=True, description='Object (target) Node ID'),
})

bbop_graph = api.model('Graph', {
    'nodes': fields.List(fields.Nested(node), description='All nodes in graph'),
    'edges': fields.List(fields.Nested(edge), description='All edges in graph'),
})


named_object = api.model('NamedObject', {
    'id': fields.String(readOnly=True, description='ID or CURIE e.g. MGI:1201606'),
    'label': fields.String(readOnly=True, description='RDFS Label'),
    'category': fields.String(readOnly=True, description='Type of object')
})

relation = api.inherit('Relation', named_object, {
})

publication = api.inherit('Publication', named_object, {
    # authors etc
})


# todo: inherits
taxon = api.model('Taxon', {
    'id': fields.String(readOnly=True, description='CURIE ID, e.g. NCBITaxon:9606'),
    'label': fields.String(readOnly=True, description='RDFS Label')
})

bio_object = api.inherit('BioObject', named_object, {
    'taxon': fields.Nested(taxon, description='Taxon to which the object belongs')
})


# Assoc

association = api.model('Association', {
    'id': fields.String(readOnly=True, description='Association/annotation unique ID'),
    'subject': fields.Nested(bio_object, description='Subject of association (what it is about), e.g. MGI:1201606'),
    'object': fields.Nested(bio_object, description='Object (sensu RDF), aka target, e.g. MP:0002109'),
    'relation': fields.Nested(relation, description='Relationship type connecting subject and object'),
    'evidence_graph': fields.Nested(bbop_graph, description='Subject-object relationship may be indirect, this graph has explicit relationships'),
    'provided_by': fields.List(fields.String, description='Provider of association TODO'),
    'publications': fields.List(fields.Nested(publication), description='Publications supporting association')
})


compact_association_set = api.model('CompactAssociationSet', {
    'subject': fields.String(description='Subject of association (what it is about), e.g. MGI:1201606'),
    'relation': fields.String(description='Relationship type connecting subject and object list'),
    'objects': fields.List(fields.String, description='List of O, for a given (S,R) pair, yielding (S,R,O) triples. E.g. list of MPs for (MGI:nnn, has_phenotype)'),
})

association_results = api.inherit('AssociationResults', search_result, {
    'associations': fields.List(fields.Nested(association), description='Complete representation of full association object, plus evidence'),
    'compact_associations': fields.List(fields.Nested(compact_association_set), description='Compact representation in which objects (e.g. phenotypes) are collected for subject-predicate pairs'),
    'objects': fields.List(fields.String, description='List of distinct objects used')
})


# Bio Objects

sequence_position = api.inherit('SequencePosition', bio_object, {
    'position': fields.Integer,
    'reference': fields.String
})

sequence_location = api.inherit('SequenceLocation', bio_object, {
    'begin': fields.Nested(sequence_position),
    'end': fields.Nested(sequence_position),
})

sequence_feature = api.inherit('SequenceFeature', bio_object, {
    'locations': fields.List(fields.Nested(sequence_location)),
    'sequence': fields.String
})

gene = api.inherit('Gene', sequence_feature, {
    'family_ids' : fields.List(fields.String)
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

# phylo
phylogenetic_node = api.inherit('PhylogeneticNode', named_object, {
    'feature': fields.Nested(sequence_feature),
    'parent_id': fields.String,
    'event': fields.String,
    'branch_length': fields.Float
})
phylogenetic_tree = api.inherit('PhylogeneticTree', named_object, {
})

# clinical
clinical_individual = api.inherit('ClinicalIndividual', named_object, {
})
