from biogolr.golr_associations import search_associations, GolrFields, select_distinct_subjects

M=GolrFields()

def test_select_distinct():
    results = select_distinct_subjects(subject_category='gene',
                                       object_category='phenotype',
                                       subject_taxon='NCBITaxon:9606')
    assert len(results) > 0

