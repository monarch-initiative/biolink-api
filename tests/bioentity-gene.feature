
Feature: bioentity routes work as expected

These routes (`bioentity`) provide a way to query for domain-specific
objects such as genes, diseases, etc, as well as for associations
between these entities

## Genes
 
 Scenario: User fetches all information on a human gene
    Given a path "/bioentity/gene/NCBIGene:84570"
     then the content should contain "COL25A1"
    when the content is converted to JSON
      then the JSON should have the top-level property "id"
      and the JSON should have a JSONPath "homology_associations[*].object"
      and the JSON should have a JSONPath "homology_associations[*].object.id"
      and the JSON should have some JSONPath "homology_associations[*].object.label" with "string" "col25a1"

 Scenario: User fetches all information on a mouse gene
    Given a path "/bioentity/gene/MGI:1342287"
     then the content should contain "Klf4"
    when the content is converted to JSON
      then the JSON should have the top-level property "id"
      and the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "abnormal Bowman membrane"

### TODO ensure label populated in scigraph call

 Scenario: User fetches all information on the same mouse gene, using an ENSEMBL ID
    Given a path "/bioentity/gene/ENSEMBL:ENSMUSG00000003032"
     then the content should contain "Klf4"
    when the content is converted to JSON
      then the JSON should have some JSONPath "phenotype_associations[*].subject.id" with "string" "MGI:1342287"
      and the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "abnormal Bowman membrane"

 Scenario: User fetches all phenotypes for a mouse gene
    Given a path "/bioentity/gene/MGI:1342287/phenotypes"
    when the content is converted to JSON
      then the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "abnormal Bowman membrane"

 Scenario: User fetches all GO functional assignments for a mouse gene
    Given a path "/bioentity/gene/MGI:1342287/function"
    when the content is converted to JSON
      then the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "GO:0048679"
      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "regulation of axon regeneration"

 Scenario: User fetches all interactions for a mouse gene
    Given a path "/bioentity/gene/MGI:1342287/interactions"
    when the content is converted to JSON
      then the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "GO:0048679"
      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "regulation of axon regeneration"

