Feature: Association queries return lists of associations

## Phenotype Associations

 Scenario: Client wants human and mouse genes with eyelid abnormalities, using a HPO ID
    Given a path "/association/find/gene/phenotype?subject_taxon=NCBITaxon:40674&object=HP:0000492&fl_excludes_evidence=true&page=1"
    when the content is converted to JSON
####      then the JSON should have some JSONPath "associations[*].object.id" with "string" "HP:0011025"

 Scenario: Client wants human and mouse genes with cardiovascular phenotypes, using an MP ID
    Given a path "/association/find/gene/phenotype?subject_taxon=NCBITaxon:40674&object=MP:0001340&fl_excludes_evidence=true&page=1"
    when the content is converted to JSON
