Feature: Anatomy association queries that return a list of associations

## Anatomy to Gene associations

    Scenario: User wants genes expressed in 'quadriceps femoris'
        Given a path "/bioentity/anatomy/UBERON:0001377/genes?rows=20"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "UBERON:0001379"
        then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "anatomical entity"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "gene"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "expressed in"

    Scenario: User wants genes expressed in 'eye' for Danio rerio
        Given a path "/bioentity/anatomy/UBERON:0000970/genes?rows=20&taxon=NCBITaxon:7955"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "anatomical entity"
        then the JSON should have some JSONPath "associations[*].object.taxon.label" with "string" "Danio rerio"
