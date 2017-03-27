from biowikidata.uniprot_sparql import seeAlso

reelin = 'UniProtKB:P78509'

def test_p2d():
    # reelin
    domains = seeAlso(reelin,db='InterPro')
    print(str(domains))
    assert 'InterPro:IPR011040' in domains
    assert(len(domains)>3)
    
