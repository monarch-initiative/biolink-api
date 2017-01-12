Feature: Disease entity queries work as expected

TODO - consider swapping subject/object

## Diseases

 Scenario: User queries for a specific form of Parkinson disease
    Given a path "/bioentity/disease/OMIM:605543/models"
     then the content should contain "Snca"
      and the content should contain "Mus musculus"
      and the content should contain "C57BL/6"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MGI:5544308"

 Scenario: User queries for worm models of supranuclear palsy
    Given a path "/bioentity/disease/DOID:678/models/NCBITaxon:6239"
     then the content should contain "wormbase"
      and the content should contain "Caenorhabditis elegans"
      and the content should contain "ptl-1"

 Scenario: User queries for dog models of lipid storage diseases (e.g. gangliosidosis)
    Given a path "/bioentity/disease/DOID:9455/models/NCBITaxon:9615"
     then the content should contain "GM11474"
      and the content should contain "Canis lupus"
      and the content should contain "Gangliosidosis"
