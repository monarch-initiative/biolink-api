Feature: bioentity routes work as expected

These routes (`bioentity`) provide a way to query for domain-specific
objects such as genes, diseases, etc, as well as for associations
between these entities

## Info about a Gene

    Scenario: User fetches all information on a human gene
        Given a path "/bioentity/gene/NCBIGene:84570"
        then the content should contain "COL25A1"
        when the content is converted to JSON
        then the JSON should have the top-level property "id"
        and the JSON should have some JSONPath "id" with "string" "HGNC:18603"

    Scenario: User fetches all information on a mouse gene
        Given a path "/bioentity/gene/MGI:1342287"
        then the content should contain "Klf4"

    Scenario: User fetches all information on the same mouse gene, using an ENSEMBL ID
        Given a path "/bioentity/gene/ENSEMBL:ENSMUSG00000003032"
        then the content should contain "Klf4"

## Gene to Homolog associations

    Scenario: User fetches all homologs of SHH
        Given a path "/bioentity/gene/NCBIGene:6469/homologs?rows=500"
        then the content should contain "Shh"
        when the content is converted to JSON
        then the JSON should have the top-level property "associations"
        and the JSON should have some JSONPath "associations[*].object.id" with "string" "MGI:98297"
        and the JSON should have some JSONPath "associations[*].object.taxon.id" with "string" "NCBITaxon:10090"


### TODO ensure label populated in scigraph call

## Gene to Phenotype associations

    Scenario: User fetches all phenotypes for a mouse gene
        Given a path "/bioentity/gene/MGI:1342287/phenotypes?rows=500"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MP:0008521"
        and the JSON should have some JSONPath "associations[*].object.label" containing "string" "abnormal Bowman membrane"

## Gene to Function associations

    Scenario: User fetches all GO functional assignments for a zebrafish gene
        Given a path "/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0030500"
        and the JSON should have some JSONPath "associations[*].object.label" with "string" "regulation of bone mineralization"

    Scenario: Map functional assignments for a gene to a to a user-specified slim
        Given a path "/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function?slim=GO%3A0001525&slim=GO%3A0048731&slim=GO%3A0005634"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].slim[*]" with "string" "GO:0048731"

## Gene to Gene Interactions

    Scenario: User fetches all interactions for a mouse gene
        Given a path "/bioentity/gene/MGI:1342287/interactions?rows=500"
        then the content should contain "https://archive.monarchinitiative.org/#biogrid"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MGI:88039"
        and the JSON should have some JSONPath "associations[*].object.label" with "string" "Apc"

## Gene to Anatomy associations

    Scenario: "User fetches anatomy terms associated with a gene"
        Given a path "/bioentity/gene/NCBIGene%3A13434/anatomy"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MGI:1274787"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "UBERON:0007769"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "expressed in"

## Gene to Genotype associations

    Scenario: "User fetches genotypes associated with a gene"
        Given a path "/bioentity/gene/HGNC:11025/genotypes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "dbSNPIndividual:19935"


## Gene to Model associations

    Scenario: "User fetches models associated with a gene"
        Given a path "/bioentity/gene/NCBIGene:17988/models"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MGI:1341799"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Ndrg1"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MMRRC:059206"

## Gene to Ortholog-Disease associations

    Scenario: "User fetches diseases from orthologs associated with a gene"
        Given a path "/bioentity/gene/NCBIGene:17988/ortholog/diseases"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "HGNC:7679"
        then the JSON should have some JSONPath "associations[*].subject.taxon.label" with "string" "Homo sapiens"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MONDO:0011085"

## Gene to Ortholog-Phenotype associations

    Scenario: "User fetches phenotypes from orthologs associated with a gene"
        Given a path "/bioentity/gene/NCBIGene:4750/ortholog/phenotypes?&facet=true"
        when the content is converted to JSON
        then the JSON should have some JSONPath "facet_counts.subject_taxon_label" containing "string" "Mus musculus"
        then the JSON should have some JSONPath "facet_counts.subject_taxon_label" containing "string" "Danio rerio"

## Gene to Pathway associations

    Scenario: "User fetches pathways associated with a gene"
        Given a path "/bioentity/gene/NCBIGene:50846/pathways"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "HGNC:2865"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "REACT:R-HSA-5658034"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "involved_in"

## Gene to Phenotype associations

    Scenario: "User fetches phenotypes associated with a gene"
        Given a path "/bioentity/gene/HGNC:11603/phenotypes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "Short femur"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "Patellar hypoplasia"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "Hip dysplasia"

## Gene to Publication associations

    Scenario: "User fetches publications associated with a gene"
        Given a path "/bioentity/gene/HGNC:11603/publications"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "PMID:19453261"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "PMID:30290780"

## Gene to Variant associations

    Scenario: "User fetches variants associated with a gene"
        Given a path "/bioentity/gene/HGNC:10896/variants"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "ClinVarVariant:570752"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "has_affected_feature"