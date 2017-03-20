from obographs.ontol_factory import OntologyFactory
from obographs.assoc_factory import AssociationSetFactory
from obographs.assocmodel import AssociationSet
import logging
import random

NUCLEUS = 'GO:0005634'

def test_construct():
    """
    factory test
    """
    ofactory = OntologyFactory()
    afactory = AssociationSetFactory()
    ont = ofactory.create('go')
    aset = afactory.create(ontology=ont,
                           subject_category='gene',
                           object_category='function',
                           taxon='NCBITaxon:10090')

    rs = aset.query([NUCLEUS],[])
    print(str(rs))
