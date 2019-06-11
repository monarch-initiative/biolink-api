Feature: Pathway association queries that return a list of associations

## Pathway to Gene associations

    Scenario: User fetches pathway to gene associations
        Given a path "/bioentity/pathway/REACT:R-HSA-5387390/genes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Hh mutants abrogate ligand secretion"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "HGNC:9555"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/ctd.ttl"

## Pathway to Phenotype associations

    Scenario: User fetches pathway to phenotype associations
        Given a path "/bioentity/pathway/REACT:R-HSA-5387390/phenotypes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Hh mutants abrogate ligand secretion"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "Dystonia"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "Pelvic girdle muscle atrophy"
