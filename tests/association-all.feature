Feature: Association queries

## General Associations

Path: `/association/find/`

Note that inference is on by default. Queries for a general taxonomic class will find associations to subclass.

 Scenario: Client queries for all annotations in rabbits (we use the NCBITaxon genus)
    Given a path "/association/find/?subject_taxon=NCBITaxon:9984&object=HP:0000707&rows=1000&fl_excludes_evidence=true&page=1"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].subject.taxon.label" with "string" "Oryctolagus cuniculus"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "Abnormal myelination"
