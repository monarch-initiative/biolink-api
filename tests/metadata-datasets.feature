Feature: Getting metadata for datasets

 Scenario: Validate metadata for datasets
    Given a path "/metadata/datasets"
     when the content is converted to JSON
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dc:Publisher"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dc:isVersionOf"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcat:distribution"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dc:creator"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dc:source"
     then the JSON should have some JSONPath "edges[*].pred" with "string" "dcat:downloadURL"
