Feature: Association queries

## General Associations

Path: `/association/find/`

Note that inference is on by default. Queries for a general taxonomic class will find associations to subclass.

# Scenario: Client queries for all annotations in rabbits (we use the NCBITaxon genus)
#    Given a path "/association/find/?subject_taxon=NCBITaxon:9984&object=HP:0000707&rows=1000&fl_excludes_evidence=true&page=1"
#    when the content is converted to JSON
#      then the JSON should have some JSONPath "associations[*].subject.taxon.label" with "string" "Oryctolagus cuniculus"
#      and the JSON should have some JSONPath "associations[*].object.label" with "string" "Abnormal myelination"


## Associations from a subject

    Scenario: Client queries for all associations from a given subject
    Given a path "/association/from/NCBIGene:84570"
    when the content is converted to JSON
    then the JSON should have some JSONPath "associations[*].subject.id" with "string" "HGNC:18603"
    then the JSON should have some JSONPath "associations[*].subject.label" with "string" "COL25A1"
    then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "gene"

    Scenario: Client queries for all associations from a given subject, constrained by relation
    Given a path "/association/from/NCBIGene:84570?relation=RO:0002331"
    then the content should not contain "colocalizes_with"
    then the content should not contain "causes condition"

## Associations to an object

    Scenario: Client queries for all associations to a given object
    Given a path "/association/to/MONDO:0014538"
    when the content is converted to JSON
    then the JSON should have some JSONPath "associations[*].subject.id" with "string" "HGNC:18603"
    then the JSON should have some JSONPath "associations[*].subject.label" with "string" "COL25A1"
    then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "gene"

