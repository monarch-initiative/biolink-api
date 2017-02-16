from obographs.sparql2ontology import *

def test_isa():
    """
    reciprocal test
    """
    r = fetchall_isa('pato')
    print(r)
    

