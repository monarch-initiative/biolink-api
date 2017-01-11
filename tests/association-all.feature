Feature: Association queries

## General Associations

Path: `/association/find/`

Note that inference is on by default. Queries for a general taxonomic class will find associations to subclass.

 Scenario: Client queries for all annotations in Monotremes (e.g. Duck billed platypus)
    Given a path "/association/find/?subject_taxon=NCBITaxon:9255&rows=10&fl_excludes_evidence=true&page=1"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].subject.taxon.label" with "string" "Ornithorhynchus anatinus"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "Asthma"
