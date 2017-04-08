from biowikidata.wd_sparql import protein_to_domain

reelin = 'UniProtKB:P78509'

def test_p2d():
    # reelin
    domains = protein_to_domain(reelin)
    print(str(domains))
    assert 'InterPro:IPR011040' in domains
    assert(len(domains)>3)
    
