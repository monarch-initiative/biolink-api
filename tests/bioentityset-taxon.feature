
Feature: homologous set of bioentities returned for a given gene all have a valid taxon

 Scenario Outline: User fetches all homologs for a human gene and they all have their taxon info
    Given a path "/bioentity/gene/<hgncID>/homologs/?homology_type=O&fetch_objects=false&rows=200"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.taxon.id" of type "string"
      and the JSON should have some JSONPath "associations[*].object.taxon.label" of type "string"
      #and the gene "associations[*].object" homolog ID should be the authoritative source for taxon

    Examples: human genes
      | hgncID  |
      | HGNC:100 |
      | HGNC:16397 |
      | HGNC:11593 |
      | HGNC:4739 |
      | HGNC:3262 |
      | HGNC:14581 |
      | HGNC:11604 |
      | HGNC:3686 |
      | HGNC:583 |
      | HGNC:7 |
      | HGNC:11730 |
      | HGNC:7881 |
      | HGNC:12774 |
      | HGNC:2908 |
      | HGNC:10848 |
      | HGNC:11773 |
      | HGNC:11998 |
      | HGNC:8620 |
      | HGNC:3009 |
      | HGNC:6769 |
