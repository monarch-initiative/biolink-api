
Feature: Monarch-app's JSON service is sane
 Monarch-app JSON blobs behave as expected for various data.
 
 @data
 Scenario: User attempts to use consume the JSON for a disease
    Given I collect data at path "/bioentity/gene/NCBIGene:84570"
     then the content should contain "COL25A1"
    when the content is converted to JSON
      then the JSON should have the top-level property "id"
      and the JSON should have a JSONPath "homology_associations[*].object"
      and the JSON should have a JSONPath "homology_associations[*].object.label"
      and the JSON should have some JSONPath "homology_associations[*].object.label" with "string" "col25a1"
