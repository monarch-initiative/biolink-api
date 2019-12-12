Feature: Getting metadata for datasets

 Scenario: Validate metadata for datasets
    Given a path "/metadata/datasets"
     when the content is converted to JSON
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcterms:Publisher"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcterms:isVersionOf"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcat:Distribution"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcterms:creator"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcterms:source"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcterms:downloadURL"

