from biowikidata.wd_sparql import doid_to_wikidata, resolve_to_wikidata, condition_to_drug

asthma = 'DOID:2841'

def test_c2d():
    # asthma
    drugs = condition_to_drug(asthma)
    print(str(drugs))
    # ephedrine
    assert 'CHEBI:15407' in drugs
    assert(len(drugs)>0)

def test_lookup():
    wdids = doid_to_wikidata(asthma)
    assert wdids == ['http://www.wikidata.org/entity/Q35869']

def test_resolve():
    wdids = resolve_to_wikidata(asthma)
    assert wdids == ['http://www.wikidata.org/entity/Q35869']
    
