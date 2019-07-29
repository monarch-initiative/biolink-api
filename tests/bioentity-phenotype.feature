Feature: Phenotype entity queries work as expected


## Info about a Phenotype

    Scenario: User queries for MP:0000087
        Given a path "/bioentity/phenotype/MP:0000087"
        then the content should contain "lower jaw"
        and the content should contain "mandible"

## Phenotype to Gene associations

    Scenario: User queries for mouse genes with abnormal Bowman membrane phenotype
        Given a path "/bioentity/phenotype/MP:0008521/genes"
        then the content should contain "Klf4"

### Phenotype to Anatomy associations

    Scenario: Client requires mapping between enlarged thymus (MP) and anatomy
        Given a path "/bioentity/phenotype/MP:0000709/anatomy"
        then the content should contain "thymus"
        and the content should contain "UBERON:0002370"

    Scenario: Client requires mapping between prominent nose (HP) and anatomy
        Given a path "/bioentity/phenotype/HP:0000448/anatomy"
        then the content should contain "nose"
        and the content should contain "UBERON:0000004"

# TODO: This will always fail until bioentity/phenotype/<id>/anatomy route is fixed
# Scenario: Client requires mapping between phenotype (ZP) and anatomy
#    Given a path "/bioentity/phenotype/ZP:0004204/anatomy"
#     then the content should contain "muscle pioneer"
#      and the content should contain "ZFA:0001086"

### Phenotype to Case associations

    Scenario: Client requires cases associated with a phenotype
        Given a path "/bioentity/phenotype/HP:0011951/cases"
        then the content should contain "Aspiration pneumonia"
        and the content should contain "MONARCH:c000009"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/udp.ttl"

### Phenotype to Disease associations

    Scenario: Client requires diseases associated with a phenotype
        Given a path "/bioentity/phenotype/HP:0011951/diseases"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Aspiration pneumonia"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "orofaciodigital syndrome IX"


### Phenotype to Genotype associations

    Scenario: Client requires genotypes associated with a phenotype
        Given a path "/bioentity/phenotype/HP:0011951/genotypes"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Recurrent aspiration pneumonia"
        then the JSON should have some JSONPath "associations[*].object.taxon.label" with "string" "Homo sapiens"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "dbSNPIndividual:15811"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "genotype"

### Phenotype to Pathway associations

    Scenario: Client requires pathways associated with a phenotype
        Given a path "/bioentity/phenotype/MP:0001569/pathways"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Neonatal hyperbilirubinemia"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "KEGG-path:maphsa00040"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "pathway"

### Phenotype to Variant associations

    Scenario: Client requires variants associated with a phenotype
        Given a path "/bioentity/phenotype/HP:0011951/variants"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Recurrent aspiration pneumonia"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "ClinVarVariant:158740"
then the JSON should have some JSONPath "associations[*].object.category" containing "string" "variant"

### Phenotype to Publication associations

    Scenario: Client requires publications associated with a phenotype
        Given a path "/bioentity/phenotype/MP:0001569/publications"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Hyperbilirubinemia"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "PMID:18059474"
then the JSON should have some JSONPath "associations[*].object.category" containing "string" "publication"
