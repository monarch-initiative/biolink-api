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

    Scenario: Client requires mapping between MP:0008521 (MP) and anatomy
        Given a path "/bioentity/phenotype/MP:0008521/anatomy"
        then the content should contain "anterior limiting lamina of cornea"
        and the content should contain "UBERON:0004370"

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


### Phenotype to Pathway associations

    Scenario: Client requires pathways associated with a phenotype
        Given a path "/bioentity/phenotype/MP:0001569/pathways?rows=50"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "decreased circulating bilirubin level"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "REACT:R-MMU-114608"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "pathway"

### Phenotype to Variant associations
    # https://github.com/monarch-initiative/monarch-ui/issues/189
    # TODO replace with gwas catalog association
    #Scenario: Client requires variants associated with a phenotype
    #    Given a path "/bioentity/phenotype/HP:0011951/variants"
    #    then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Recurrent aspiration pneumonia"
    #   then the JSON should have some JSONPath "associations[*].object.id" with "string" "ClinVarVariant:2587"
    #   then the JSON should have some JSONPath "associations[*].object.category" containing "string" "variant"

### Phenotype to Publication associations

    Scenario: Client requires publications associated with a phenotype
        Given a path "/bioentity/phenotype/MP:0001569/publications"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Hyperbilirubinemia"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "PMID:18059474"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "publication"
