Feature: Disease entity queries work as expected

TODO - consider swapping subject/object

## Models

 Scenario: User queries for a specific form of episodic ataxia disease
    Given a path "/bioentity/disease/OMIM:160120/models"
     then the content should contain "Kcna1"
      and the content should contain "Mus musculus"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MGI:2655686"

 Scenario: User queries for worm models of supranuclear palsy
    Given a path "/bioentity/disease/DOID:678/models/NCBITaxon:6237"
     then the content should contain "wormbase"
      and the content should contain "Caenorhabditis"
      and the content should contain "ptl-1"

 Scenario: User queries for dog models of lipid storage diseases (e.g. gangliosidosis)
    Given a path "/bioentity/disease/DOID:9455/models/NCBITaxon:9615"
     then the content should contain "GM11474"
      and the content should contain "Canis lupus"
      and the content should contain "Gangliosidosis"

 Scenario: User queries for Parkinson disease, late-onset and can see onset and inheritance
    Given a path "/bioentity/disease/MONDO:0008199"
     when the content is converted to JSON
      then the JSON should have some JSONPath "clinical_modifiers[*].id" with "string" "HP:0003676"
      then the JSON should have some JSONPath "clinical_modifiers[*].label" with "string" "Progressive"
      then the JSON should have some JSONPath "inheritance[*].id" with "string" "HP:0003745"
      then the JSON should have some JSONPath "inheritance[*].label" with "string" "Sporadic"

### Genes

 Scenario: User queries for genes associated with lipid storage diseases (e.g. gangliosidosis)
    Given a path "/bioentity/disease/DOID:9455/genes?rows=0&fetch_objects=true"
     then the content should contain "NCBIGene:1051"
