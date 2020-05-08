Feature: Pathway association queries that return a list of associations

## Pathway to Gene associations

    Scenario: User fetches pathway to gene associations
        Given a path "/bioentity/pathway/REACT:R-HSA-879415/genes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Advanced glycosylation endproduct receptor signaling"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "HGNC:9411"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://archive.monarchinitiative.org/#reactome"
        
