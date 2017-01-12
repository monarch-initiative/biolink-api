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

abstract_property_value = api.model('AbstractPropertyValue', {
    'val': fields.String(readOnly=True, description='value part'),
    'pred': fields.String(readOnly=True, description='predicate (attribute) part'),
    'xrefs': fields.List(fields.String, description='Xrefs provenance for property-value'),
})

synonym_property_value = api.inherit('SynonymPropertyValue', abstract_property_value, {
})

association_property_value = api.inherit('AssociationPropertyValue', abstract_property_value, {
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

bbop_graph = api.model('Graph', {
    'nodes': fields.List(fields.Nested(node), description='All nodes in graph'),
    'edges': fields.List(fields.Nested(edge), description='All edges in graph'),
})

named_object = api.model('NamedObject', {
    'id': fields.String(readOnly=True, description='ID or CURIE e.g. MGI:1201606'),
    'label': fields.String(readOnly=True, description='RDFS Label'),
    'categories': fields.List(fields.String(readOnly=True, description='Type of object')),
    'synonyms': fields.List(fields.Nested(synonym_property_value), description='list of synonyms or alternate labels')
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

annotation_extension = api.model('AnnotationRelation', {
    'relation_chain': fields.List(fields.Nested(relation, description='Relationship type. If more than one value, interpreted as chain')),
    'filler': fields.Nested(named_object, description='Extension interpreted as OWL expression (r1 some r2 some .. some filler'),
})

association = api.model('Association', {
    'id': fields.String(readOnly=True, description='Association/annotation unique ID'),
    'type': fields.String(readOnly=True, description='Type of association, e.g. gene-phenotype'),
    'subject': fields.Nested(bio_object, description='Subject of association (what it is about), e.g. ClinVar:nnn, MGI:1201606'),
    'subject_extension': fields.List(fields.Nested(annotation_extension, description='Additional properties of the subject in the context of this association')),
    'object': fields.Nested(bio_object, description='Object (sensu RDF), aka target, e.g. HP:0000448, MP:0002109, DOID:14330'),
    'object_extension': fields.List(fields.Nested(annotation_extension, description='Additional properties of the object in the context of this association')),
    'relation': fields.Nested(relation, description='Relationship type connecting subject and object'),
    'qualifiers': fields.List(fields.Nested(association_property_value, description='Qualifier on the association')),
    'evidence_graph': fields.Nested(bbop_graph, description='Subject-object relationship may be indirect, this graph has explicit relationships'),
    'evidence_types': fields.List(fields.Nested(named_object, description='Evidence types (ECO classes) extracted from evidence graph')),
    'provided_by': fields.List(fields.String, description='Provider of association, e.g. Orphanet, ClinVar'),
    'publications': fields.List(fields.Nested(publication), description='Publications supporting association, extracted from evidence graph')
})

# For example, via homology
chained_association = api.model('ChainedAssociation', {
    'proximal_association': fields.Nested(association, description='immediate association, between subject and intermediate object'),
    'distal_associations': fields.List(fields.Nested(association), description='Associations where the intermediate object is the subject')
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

sequence_position = api.model('SequencePosition', {
    'position': fields.Integer,
    'reference': fields.String
})

sequence_location = api.inherit('SequenceLocation', bio_object, {
    'begin': fields.Nested(sequence_position),
    'end': fields.Nested(sequence_position),
})

sequence_feature = api.inherit('SequenceFeature', bio_object, {
    'locations': fields.List(fields.Nested(sequence_location)),
    'sequence': fields.String,
    'homology_associations': fields.List(fields.Nested(association)),
})

gene = api.inherit('Gene', sequence_feature, {
    'families' : fields.List(fields.Nested(named_object), description='Families, superfamilies etc to which these gene belongs'),
    'phenotype_associations': fields.List(fields.Nested(association)),
    'disease_associations': fields.List(fields.Nested(association)),
    'homology_associations': fields.List(fields.Nested(association)),
    'function_associations': fields.List(fields.Nested(association)),
    'genotype_associations': fields.List(fields.Nested(association)),
    #'genotypes': fields.List(fields.Nested(bio_object), desc='List of references to genotype objects')
})

gene_product = api.inherit('GeneProduct', sequence_feature, {
    'genes': fields.List(fields.Nested(gene))
})

transcript = api.inherit('Transcript', sequence_feature, {
    'genes': fields.List(fields.Nested(gene))
})

# in GENO, this corresponds to (genotype OR part-of some genotype)
genotype = api.inherit('Genotype', sequence_feature, {
    #'genes': fields.List(fields.Nested(bio_object), desc='List of references to gene object'),
    'phenotype_associations': fields.List(fields.Nested(association)),
    'disease_associations': fields.List(fields.Nested(association)),
    'gene_associations': fields.List(fields.Nested(association)),
    'variant_associations': fields.List(fields.Nested(association)),
})

allele = api.inherit('Allele', genotype, {
})

# molecular entities
molecular_complex = api.inherit('MolecularComplex', bio_object, {
    'genes': fields.List(fields.Nested(gene))
})

substance = api.inherit('Substance', bio_object, {
    'target_associations': fields.List(fields.Nested(association)),
    'inchi': fields.List(fields.String),
    'inchi_key': fields.List(fields.String),
    'smiles': fields.List(fields.String),
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
