from biowikidata.wd_sparql import neighbors

reelin = 'UniProtKB:P78509'

def test_generic():
    # reelin
    assocs = neighbors(reelin,subject_category='protein',object_category='domain')
    print(str(assocs))
    domains = [a['object'] for a in assocs]
    assert 'InterPro:IPR011040' in domains
    assert(len(domains)>3)
    
