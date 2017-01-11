Feature: Association queries work as expected

## Gene-Phenotype Associations

 Scenario: User queries for mouse genes with abnormal Bowman membrane phenotype
    Given a path "/association/find/gene/phenotype/?subject_taxon=NCBITaxon:10090&rows=10&object=MP:0008521"
     then the content should contain "abnormal Bowman membrane"
    when the content is converted to JSON
      then the JSON should have some JSONPath "phenotype_associations[*].subject.id" with "string" "MGI:1342287"
      and the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "abnormal Bowman membrane"
