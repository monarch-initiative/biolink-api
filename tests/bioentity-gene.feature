
Feature: bioentity routes work as expected

These routes (`bioentity`) provide a way to query for domain-specific
objects such as genes, diseases, etc, as well as for associations
between these entities

## Genes
 
 Scenario: User fetches all information on a human gene
    Given a path "/bioentity/gene/NCBIGene:84570"
     then the content should contain "COL25A1"
    when the content is converted to JSON
      then the JSON should have the top-level property "id"
      and the JSON should have a JSONPath "homology_associations[*].object"
      and the JSON should have a JSONPath "homology_associations[*].object.id"
      and the JSON should have some JSONPath "homology_associations[*].object.label" with "string" "col25a1"

 Scenario: User fetches all information on a mouse gene
    Given a path "/bioentity/gene/MGI:1342287"
     then the content should contain "Klf4"
#    when the content is converted to JSON
#      then the JSON should have the top-level property "id"
#      and the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "MP:0008521"
#      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "abnormal Bowman membrane"

## Homologs
 Scenario: User fetches paralogs of SHH
    Given a path "/bioentity/gene/NCBIGene:6469/homologs/?homology_type=P"
     then the content should contain "DHH"
    when the content is converted to JSON
      then the JSON should have the top-level property "associations"
      and the JSON should have some JSONPath "associations[*].object.id" with "string" "NCBIGene:50846"
      and the JSON should have some JSONPath "associations[*].object.taxon.label" with "string" "Homo sapiens"

 Scenario: User fetches homologs of SHH with taxon Homo sapiens
    Given a path "/bioentity/gene/NCBIGene:6469/homologs/?homolog_taxon=NCBITaxon:9606"
     then the content should contain "DHH"
    when the content is converted to JSON
      then the JSON should have the top-level property "associations"
      and the JSON should have some JSONPath "associations[*].object.id" with "string" "NCBIGene:50846"
      and the JSON should have some JSONPath "associations[*].object.taxon.label" with "string" "Homo sapiens"

 Scenario: User fetches all homologs of SHH
    Given a path "/bioentity/gene/NCBIGene:6469/homologs/"
     then the content should contain "Shh"
    when the content is converted to JSON
      then the JSON should have the top-level property "associations"
      and the JSON should have some JSONPath "associations[*].object.id" with "string" "MGI:98297"
      and the JSON should have some JSONPath "associations[*].object.taxon.id" with "string" "NCBITaxon:10090"


### TODO ensure label populated in scigraph call

 Scenario: User fetches all information on the same mouse gene, using an ENSEMBL ID
    Given a path "/bioentity/gene/ENSEMBL:ENSMUSG00000003032"
     then the content should contain "Klf4"
    when the content is converted to JSON
      then the JSON should have some JSONPath "phenotype_associations[*].subject.id" with "string" "MGI:1342287"
#      and the JSON should have some JSONPath "phenotype_associations[*].object.id" with "string" "MP:0008521"
#      and the JSON should have some JSONPath "phenotype_associations[*].object.label" with "string" "abnormal Bowman membrane"

 Scenario: User fetches all phenotypes for a mouse gene
    Given a path "/bioentity/gene/MGI:1342287/phenotypes?rows=500"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.id" with "string" "MP:0008521"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "abnormal Bowman membrane"

 Scenario: User fetches all GO functional assignments for a zebrafish gene
    Given a path "/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0030500"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "regulation of bone mineralization"

 Scenario: Map functional assignments for a gene to a to a user-specified slim
    Given a path "/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function?slim=GO%3A0001525&slim=GO%3A0048731&slim=GO%3A0005634"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].slim[*]" with "string" "GO:0048731"

 Scenario: User fetches all interactions for a mouse gene
    Given a path "/bioentity/gene/MGI:1342287/interactions"
     then the content should contain "http://data.monarchinitiative.org/ttl/biogrid.ttl"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.id" with "string" "MGI:88039"
      and the JSON should have some JSONPath "associations[*].object.label" with "string" "Apc"

## Diseases

# Scenario: User fetches all diseases for a gene using its orphanet ID
#    Given a path "/bioentity/gene/Orphanet:173505/diseases?rows=5000"
#     then the content should contain "http://data.monarchinitiative.org/ttl/omim.ttl"
#     then the content should contain "http://data.monarchinitiative.org/ttl/ctd.ttl"
#     then the content should contain "http://data.monarchinitiative.org/ttl/orphanet.ttl"
#    when the content is converted to JSON
#      then the JSON should have some JSONPath "associations[*].subject.label" with "string" "SLC6A20"
#      and the JSON should have some JSONPath "associations[*].object.id" with "string" "OMIM:138500"
