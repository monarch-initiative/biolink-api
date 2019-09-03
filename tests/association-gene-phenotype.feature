Feature: Association queries work as expected

## Gene-Phenotype Associations

 Scenario: User queries for mouse genes with abnormal Bowman membrane phenotype
    Given a path "/association/find/gene/phenotype/?subject_taxon=NCBITaxon:10090&rows=10&object=MP:0008521"
     then the content should contain "abnormal Bowman membrane"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MGI:1342287"
      and the JSON should have some JSONPath "associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "associations[*].object.label" containing "string" "abnormal Bowman membrane"

 Scenario: User queries for mouse genes with cornea phenotypes (including subtypes in the ontology), omitting evidence
    Given a path "/association/find/gene/phenotype/?subject_taxon=NCBITaxon:10090&rows=1000&fl_excludes_evidence=true&object=MP:0008521"
     then the content should contain "abnormal Bowman membrane"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MGI:1342287"
      and the JSON should have some JSONPath "associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "associations[*].object.label" containing "string" "abnormal Bowman membrane"


 Scenario: User queries for mouse genes with cornea phenotypes (using an HPO ID), omitting evidence
    Given a path "/association/find/gene/phenotype/?subject_taxon=NCBITaxon:10090&rows=1000&fl_excludes_evidence=true&object=HP:0000481"
     then the content should contain "Abnormality of corneal thickness"
      and the content should contain "abnormal Bowman membrane"
