class AbstractPropertyValue():
    def __init__(self, val, pred=None, xrefs=None):
        self.val = val
        self.pred = pred
        self.xrefs=xrefs
        
class SynonymPropertyValue(AbstractPropertyValue):
    def __init__(self, val, **kwargs):
        super(SynonymPropertyValue, self).__init__(val, **kwargs)
    
class NamedObject():
    def __init__(self, id, label=None, categories=None, synonyms=None, xrefs=None):
        self.id = id
        self.label = label
        self.categories = categories
        self.synonyms = synonyms
        self.xrefs = xrefs

class TaxonClass(NamedObject):
    def __init__(self, **kwargs):
        super(TaxonClass, self).__init__(**kwargs)

class BioObject(NamedObject):
    def __init__(self, id, taxon=None, **kwargs):
        super(BioObject, self).__init__(id, **kwargs)
        self.taxon = taxon

class Gene(BioObject):
    def __init__(self, id,
                 phenotype_associations=None,
                 disease_associations=None,
                 homology_associations=None,
                 genotype_associations=None,
                 **kwargs):
        super(Gene, self).__init__(id, **kwargs)
        self.phenotype_associations = phenotype_associations
        self.disease_associations = disease_associations
        self.homology_associations = homology_associations
        self.genotype_associations = genotype_associations

class Genotype(BioObject):
    def __init__(self, id,
                 phenotype_associations=None,
                 disease_associations=None,
                 gene_associations=None,
                 **kwargs):
        super(Genotype, self).__init__(id, **kwargs)
        self.phenotype_associations = phenotype_associations
        self.disease_associations = disease_associations
        self.gene_associations = gene_associations
        
