from biogolr.golr_associations import search_associations, search_associations_compact, GolrFields, select_distinct_subjects, get_objects_for_subject, get_subjects_for_object

M=GolrFields()

HUMAN_SHH = 'NCBIGene:6469'
HOLOPROSENCEPHALY = 'HP:0001360'
TWIST_ZFIN = 'ZFIN:ZDB-GENE-050417-357'
DVPF = 'GO:0009953'

def test_go_assocs():
    results = search_associations(subject=TWIST_ZFIN,
                                  slim=['GO:0001525','GO:0048731','GO:0005634'],
                                  object_category='function')

    assocs = results['associations']
    assert len(assocs) > 0
    n_found = 0
    for r in assocs:
        print("Direct: {} Slimmed: {}".format(r['object'],r['slim']))
        if 'GO:0002040' == r['object']['id']:
            if 'GO:0048731' in r['slim']:
                n_found = n_found+1
    assert n_found == 1

    
