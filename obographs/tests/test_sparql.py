from obographs.sparql2ontology import *
from networkx.algorithms.dag import ancestors

PLOIDY = 'PATO:0001374'
def test_edges():
    """
    reconstitution test
    """
    #r = fetchall_svf('pato')
    g = get_digraph('pato')
    info = g.node[PLOIDY]
    print(str(info))
    nodes = g.nodes()
    print(len(nodes))
    nbrs = g.neighbors(PLOIDY)
    print(str(nbrs))
    print(str(g.predecessors(PLOIDY)))
    print(str(ancestors(g, PLOIDY)))
    #g.ancestors(
    print(g)
    

