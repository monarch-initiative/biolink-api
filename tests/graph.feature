Feature: graph routes work as expected

These routes (`node`) provide a way to query basic information
  about an entity (synonyms, type, taxon) and its neighborhood

## Info about a node

    Scenario: User fetches all information on a human gene
        Given a path "/graph/node/NCBIGene:84570"
        then the JSON should have some JSONPath "label" with "string" "COL25A1"
        and the JSON should have some JSONPath "id" with "string" "HGNC:18603"

## Info about a nodes neighborhood

    Scenario: User fetches neighborhood for disease
        Given a path "/graph/edges/from/OMIM:130010"
        then the JSON should have some JSONPath "nodes" of type "array"
        and the JSON should have some JSONPath "edges" of type "array"
        and the JSON should have some JSONPath "edges[*].pred" containing "string" "subClassOf"
        and the JSON should have some JSONPath "nodes[*].id" containing "string" "MONDO:0019568"
