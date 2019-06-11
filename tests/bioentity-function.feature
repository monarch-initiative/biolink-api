Feature: bioentity function (GO) routes work as expected

## Gene to Function associations

    Scenario: User fetches all GO functional assignments for a zebrafish gene
        Given a path "/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function?rows=100"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0030500"
        and the JSON should have some JSONPath "associations[*].object.label" with "string" "regulation of bone mineralization"

    Scenario: User fetches all GO functional assignments for a human gene using a NCBI ID, note GO may annotate to UniProt
        Given a path "/bioentity/gene/NCBIGene:6469/function?rows=100"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0001755"
        and the JSON should have some JSONPath "associations[*].object.label" with "string" "neural crest cell migration"

    Scenario: User fetches all GO functional assignments for a human gene using a HGNC ID, note GO may annotate to UniProt
        Given a path "/bioentity/gene/HGNC:6081/function?rows=100"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0005158"
        and the JSON should have some JSONPath "associations[*].object.label" with "string" "insulin receptor binding"

## Function to Gene associations

## Function to Publication associations

## Taxon association with a function term
# TODO: After the relevant routes are fixed
