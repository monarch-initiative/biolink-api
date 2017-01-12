from prefixcommons.curie_util import expand_uri, contract_uri, NoPrefix

bp_id = "GO:0008150"
bp_iri = "http://purl.obolibrary.org/obo/GO_0008150"

def test_prefixes():
    assert contract_uri(bp_iri) == [bp_id]
    assert expand_uri(bp_id) == bp_iri
    assert contract_uri("FAKE", strict=False) == []
    try:
        contract_uri("FAKE", strict=True)
    except NoPrefix as e:
        pass
    else:
        assert False



