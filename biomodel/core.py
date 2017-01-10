class SearchResult():
    """
    SearchResult

    Arguments
    ---------
     numFound : 

         total number of associations matching query

     start : 

         Cursor position

     facet_counts : 

         Mapping between field names and association counts

    """
    def __init__(self,
                 id=None,
                 numFound=None,
                 start=None,
                 facet_counts=None,
                 **kwargs):
        self.id=id
        self.numFound=numFound
        self.start=start
        self.facet_counts=facet_counts


class AbstractPropertyValue():
    """
    AbstractPropertyValue

    Arguments
    ---------
     val : 

         value part

     pred : 

         predicate (attribute) part

     xrefs : 

         Xrefs provenance for property-value

    """
    def __init__(self,
                 id=None,
                 val=None,
                 pred=None,
                 xrefs=None,
                 **kwargs):
        self.id=id
        self.val=val
        self.pred=pred
        self.xrefs=xrefs


class SynonymPropertyValue(AbstractPropertyValue):
    """
    SynonymPropertyValue

    Superclass: AbstractPropertyValue

    Arguments
    ---------
    """
    def __init__(self,
                 id=None,
                 **kwargs):
        super(SynonymPropertyValue, self).__init__(id, **kwargs)


class Node():
    """
    Node

    Arguments
    ---------
     lbl : 

         human readable label, maps to rdfs:label

    """
    def __init__(self,
                 id=None,
                 lbl=None,
                 **kwargs):
        self.id=id
        self.lbl=lbl


class Edge():
    """
    Edge

    Arguments
    ---------
     sub : 

         Subject (source) Node ID

     pred : 

         Predicate (relation) ID

     obj : 

         Object (target) Node ID

    """
    def __init__(self,
                 id=None,
                 sub=None,
                 pred=None,
                 obj=None,
                 **kwargs):
        self.id=id
        self.sub=sub
        self.pred=pred
        self.obj=obj


class Graph():
    """
    Graph

    Arguments
    ---------
     nodes : 

         All nodes in graph

     edges : 

         All edges in graph

    """
    def __init__(self,
                 id=None,
                 nodes=None,
                 edges=None,
                 **kwargs):
        self.id=id
        self.nodes=nodes
        self.edges=edges


class NamedObject():
    """
    NamedObject

    Arguments
    ---------
     label : 

         RDFS Label

     categories : 

         Type of object

     synonyms : 

         list of synonyms or alternate labels

    """
    def __init__(self,
                 id=None,
                 label=None,
                 categories=None,
                 synonyms=None,
                 **kwargs):
        self.id=id
        self.label=label
        self.categories=categories
        self.synonyms=synonyms


class Relation(NamedObject):
    """
    Relation

    Superclass: NamedObject

    Arguments
    ---------
    """
    def __init__(self,
                 id=None,
                 **kwargs):
        super(Relation, self).__init__(id, **kwargs)


class Publication(NamedObject):
    """
    Publication

    Superclass: NamedObject

    Arguments
    ---------
    """
    def __init__(self,
                 id=None,
                 **kwargs):
        super(Publication, self).__init__(id, **kwargs)


class Taxon():
    """
    Taxon

    Arguments
    ---------
     label : 

         RDFS Label

    """
    def __init__(self,
                 id=None,
                 label=None,
                 **kwargs):
        self.id=id
        self.label=label


class BioObject(NamedObject):
    """
    BioObject

    Superclass: NamedObject

    Arguments
    ---------
     taxon : 

         Taxon to which the object belongs

    """
    def __init__(self,
                 id=None,
                 taxon=None,
                 **kwargs):
        super(BioObject, self).__init__(id, **kwargs)
        self.taxon=taxon


class Association():
    """
    Association

    Arguments
    ---------
     subject : 

         Subject of association (what it is about), e.g. MGI:1201606

     object : 

         Object (sensu RDF), aka target, e.g. MP:0002109

     relation : 

         Relationship type connecting subject and object

     evidence_graph : 

         Subject-object relationship may be indirect, this graph has explicit relationships

     provided_by : 

         Provider of association TODO

     publications : 

         Publications supporting association

    """
    def __init__(self,
                 id=None,
                 subject=None,
                 object=None,
                 relation=None,
                 evidence_graph=None,
                 provided_by=None,
                 publications=None,
                 **kwargs):
        self.id=id
        self.subject=subject
        self.object=object
        self.relation=relation
        self.evidence_graph=evidence_graph
        self.provided_by=provided_by
        self.publications=publications


class CompactAssociationSet():
    """
    CompactAssociationSet

    Arguments
    ---------
     subject : 

         Subject of association (what it is about), e.g. MGI:1201606

     relation : 

         Relationship type connecting subject and object list

     objects : 

         List of O, for a given (S,R) pair, yielding (S,R,O) triples. E.g. list of MPs for (MGI:nnn, has_phenotype)

    """
    def __init__(self,
                 id=None,
                 subject=None,
                 relation=None,
                 objects=None,
                 **kwargs):
        self.id=id
        self.subject=subject
        self.relation=relation
        self.objects=objects


class AssociationResults(SearchResult):
    """
    AssociationResults

    Superclass: SearchResult

    Arguments
    ---------
     associations : 

         Complete representation of full association object, plus evidence

     compact_associations : 

         Compact representation in which objects (e.g. phenotypes) are collected for subject-predicate pairs

     objects : 

         List of distinct objects used

    """
    def __init__(self,
                 id=None,
                 associations=None,
                 compact_associations=None,
                 objects=None,
                 **kwargs):
        super(AssociationResults, self).__init__(id, **kwargs)
        self.associations=associations
        self.compact_associations=compact_associations
        self.objects=objects


class SequencePosition():
    """
    SequencePosition

    Arguments
    ---------
     position : 

     reference : 

    """
    def __init__(self,
                 id=None,
                 position=None,
                 reference=None,
                 **kwargs):
        self.id=id
        self.position=position
        self.reference=reference


class SequenceLocation(BioObject):
    """
    SequenceLocation

    Superclass: BioObject

    Arguments
    ---------
     begin : 

     end : 

    """
    def __init__(self,
                 id=None,
                 begin=None,
                 end=None,
                 **kwargs):
        super(SequenceLocation, self).__init__(id, **kwargs)
        self.begin=begin
        self.end=end


class SequenceFeature(BioObject):
    """
    SequenceFeature

    Superclass: BioObject

    Arguments
    ---------
     locations : 

     sequence : 

     homology_associations : 

    """
    def __init__(self,
                 id=None,
                 locations=None,
                 sequence=None,
                 homology_associations=None,
                 **kwargs):
        super(SequenceFeature, self).__init__(id, **kwargs)
        self.locations=locations
        self.sequence=sequence
        self.homology_associations=homology_associations


class Gene(SequenceFeature):
    """
    Gene

    Superclass: SequenceFeature

    Arguments
    ---------
     phenotype_associations : 

     disease_associations : 

     homology_associations : 

     function_associations : 

     genotype_associations : 

    """
    def __init__(self,
                 id=None,
                 phenotype_associations=None,
                 disease_associations=None,
                 homology_associations=None,
                 function_associations=None,
                 genotype_associations=None,
                 **kwargs):
        super(Gene, self).__init__(id, **kwargs)
        self.phenotype_associations=phenotype_associations
        self.disease_associations=disease_associations
        self.homology_associations=homology_associations
        self.function_associations=function_associations
        self.genotype_associations=genotype_associations


class GeneProduct(SequenceFeature):
    """
    GeneProduct

    Superclass: SequenceFeature

    Arguments
    ---------
     genes : 

    """
    def __init__(self,
                 id=None,
                 genes=None,
                 **kwargs):
        super(GeneProduct, self).__init__(id, **kwargs)
        self.genes=genes


class Transcript(SequenceFeature):
    """
    Transcript

    Superclass: SequenceFeature

    Arguments
    ---------
     genes : 

    """
    def __init__(self,
                 id=None,
                 genes=None,
                 **kwargs):
        super(Transcript, self).__init__(id, **kwargs)
        self.genes=genes


class Genotype(SequenceFeature):
    """
    Genotype

    Superclass: SequenceFeature

    Arguments
    ---------
     phenotype_associations : 

     disease_associations : 

     gene_associations : 

     variant_associations : 

    """
    def __init__(self,
                 id=None,
                 phenotype_associations=None,
                 disease_associations=None,
                 gene_associations=None,
                 variant_associations=None,
                 **kwargs):
        super(Genotype, self).__init__(id, **kwargs)
        self.phenotype_associations=phenotype_associations
        self.disease_associations=disease_associations
        self.gene_associations=gene_associations
        self.variant_associations=variant_associations


class Allele(Genotype):
    """
    Allele

    Superclass: Genotype

    Arguments
    ---------
    """
    def __init__(self,
                 id=None,
                 **kwargs):
        super(Allele, self).__init__(id, **kwargs)


class MolecularComplex(BioObject):
    """
    MolecularComplex

    Superclass: BioObject

    Arguments
    ---------
     genes : 

    """
    def __init__(self,
                 id=None,
                 genes=None,
                 **kwargs):
        super(MolecularComplex, self).__init__(id, **kwargs)
        self.genes=genes


class Substance(BioObject):
    """
    Substance

    Superclass: BioObject

    Arguments
    ---------
     target_associations : 

     inchi : 

     inchi_key : 

     smiles : 

    """
    def __init__(self,
                 id=None,
                 target_associations=None,
                 inchi=None,
                 inchi_key=None,
                 smiles=None,
                 **kwargs):
        super(Substance, self).__init__(id, **kwargs)
        self.target_associations=target_associations
        self.inchi=inchi
        self.inchi_key=inchi_key
        self.smiles=smiles


class PhylogeneticNode(NamedObject):
    """
    PhylogeneticNode

    Superclass: NamedObject

    Arguments
    ---------
     feature : 

     parent_id : 

     event : 

     branch_length : 

    """
    def __init__(self,
                 id=None,
                 feature=None,
                 parent_id=None,
                 event=None,
                 branch_length=None,
                 **kwargs):
        super(PhylogeneticNode, self).__init__(id, **kwargs)
        self.feature=feature
        self.parent_id=parent_id
        self.event=event
        self.branch_length=branch_length


class PhylogeneticTree(NamedObject):
    """
    PhylogeneticTree

    Superclass: NamedObject

    Arguments
    ---------
    """
    def __init__(self,
                 id=None,
                 **kwargs):
        super(PhylogeneticTree, self).__init__(id, **kwargs)


class ClinicalIndividual(NamedObject):
    """
    ClinicalIndividual

    Superclass: NamedObject

    Arguments
    ---------
    """
    def __init__(self,
                 id=None,
                 **kwargs):
        super(ClinicalIndividual, self).__init__(id, **kwargs)


