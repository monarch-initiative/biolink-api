from biogolr.golr_associations import fetch_bioentity


HUMAN_SHH = 'NCBIGene:6469'
HOLOPROSENCEPHALY = 'HP:0001360'
TWIST_ZFIN = 'ZFIN:ZDB-GENE-050417-357'
DVPF = 'GO:0009953'

def test_fetch():
    results = fetch_bioentity(TWIST_ZFIN)
    print(str(results))
    assert len(results) > 0

