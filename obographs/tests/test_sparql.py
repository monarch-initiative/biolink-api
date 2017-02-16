from obographs.sparql2ontology import *

def test_edges():
    """
    reconstitution test
    """
    #r = fetchall_svf('pato')
    r = get_digraph('pato')
    print(r)
    

