Feature: Get associations for any given Bioentity

## Fetch all associations for a given Bioentity

    Scenario: "User fetches all associations for a given bioentity"
        Given a path "/bioentity/HGNC%3A1103/associations?rows=500"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "gene"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "NCBIGene:6046"

## Get basic information about a Bioentity type

    Scenario: "User fetches basic info about a given bioentity"
        Given a path "/bioentity/NCBIGene%3A84570"
        when the content is converted to JSON
        then the JSON should have some JSONPath "taxon.label" with "string" "Homo sapiens"
        then the JSON should have some JSONPath "id" with "string" "HGNC:18603"
        then the JSON should have some JSONPath "label" with "string" "COL25A1"

## Get basic information about a Bioentity type, with association counts

    Scenario: "User fetches info, along with association counts, about a given bioentity"
        Given a path "/bioentity/gene/NCBIGene%3A84570?get_association_counts=true"
        when the content is converted to JSON
        then the JSON should have some JSONPath "taxon.label" with "string" "Homo sapiens"
        then the JSON should have some JSONPath "id" with "string" "HGNC:18603"
        then the JSON should have some JSONPath "label" with "string" "COL25A1"
        then the JSON should have JSONPath "association_counts.interaction.counts" greater than "integer" "10"
