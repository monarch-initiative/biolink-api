from biogolr.golr_associations import search_associations, GolrFields, select_distinct_subjects

M=GolrFields()

HUMAN_SHH = 'NCBIGene:6469'
HOLOPROSENCEPHALY = 'HP:0001360'
TWIST_ZFIN = 'ZFIN:ZDB-GENE-050417-357'
DVPF = 'GO:0009953'

def test_select_distinct():
    results = select_distinct_subjects(subject_category='gene',
                                       object_category='phenotype',
                                       subject_taxon='NCBITaxon:9606')
    assert len(results) > 0

def test_go_assocs():
    results = search_associations(subject=TWIST_ZFIN,
                                  object_category='function'
    )
    assert len(results) > 0

def test_pheno_assocs():
    results = search_associations(subject=TWIST_ZFIN,
                                  object_category='phenotype'
    )
    assert len(results) > 0

def test_pheno_objects():
    results = search_associations(subject=TWIST_ZFIN,
                                  fetch_objects=True,
                                  rows=0,
                                  object_category='phenotype'
    )
    objs = results['objects']
    assert len(objs) > 1

def test_func_objects():
    results = search_associations(subject=TWIST_ZFIN,
                                  fetch_objects=True,
                                  rows=0,
                                  object_category='function'
    )
    objs = results['objects']
    assert DVPF in objs
    assert len(objs) > 1
    
def test_pheno_objects_shh():
    results = search_associations(subject=HUMAN_SHH,
                                  fetch_objects=True,
                                  rows=0,
                                  object_category='phenotype'
    )
    objs = results['objects']
    print(objs)
    assert HOLOPROSENCEPHALY in objs
    assert len(objs) > 50
    
def test_disease_assocs():
    results = search_associations(subject=TWIST_ZFIN,
                                  object_category='disease'
    )
    assert len(results) > 0
    
