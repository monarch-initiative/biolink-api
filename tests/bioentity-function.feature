
Feature: bioentity function (GO) routes work as expected

 Scenario: User fetches all GO functional assignments for a zebrafish gene
    Given a path "/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function?rows=100"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0030500"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "regulation of bone mineralization"

 Scenario: User fetches all GO functional assignments for a human gene using a NCBI ID, not GO may annotate to UniProt
    Given a path "/bioentity/gene/NCBIGene:6469/function?rows=100"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0001755"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "neural crest cell migration"

