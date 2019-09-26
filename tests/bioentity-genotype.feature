Feature: Genotype association queries that return a list of associations

## Info about a Genotype

    Scenario: User fetches all information about a genotype
        Given a path "/bioentity/genotype/dbSNPIndividual:11441"
        then the content should contain "GM10874"
        when the content is converted to JSON

## Genotype to Case associations

    Scenario: User fetches genotype to case associations
        Given a path "/bioentity/genotype/dbSNPIndividual%3A10440/cases"
        then the content should contain "GM01793"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "BNODE:person-119-2"
        then the JSON should have some JSONPath "associations[*].object.taxon.label" with "string" "Homo sapiens"


## Genotype to Disease associations

    Scenario: User fetches genotype to case associations
        Given a path "/bioentity/genotype/dbSNPIndividual%3A10440/diseases"
        then the content should contain "GM01793"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MONDO:0005090"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "has phenotype"

## Genotype to Gene associations

    Scenario: User fetches genotype to gene associations
        Given a path "/bioentity/genotype/ZFIN:ZDB-FISH-150901-6607/genes"
        then the content should contain "shha<tbx392>"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "shha"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "shha"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/zfin.ttl"

## Genotype to Model associations

    Scenario: User fetches genotype to gene associations
        Given a path "/bioentity/genotype/BNODE:genoGM25367/models"
        then the content should contain "GM25367"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "Coriell:GM25367"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "has_genotype"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/coriell.ttl"

## Genotype to Phenotype associations

    Scenario: User fetches genotype to gene associations
        Given a path "/bioentity/genotype/BNODE:genoGM25367/phenotypes"
        then the content should contain "GM25367"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "HP:0000680"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/coriell.ttl"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/hpoa.ttl"

## Genotype to Publication associations

    Scenario: User fetches genotype to publication associations
        Given a path "/bioentity/genotype/ZFIN:ZDB-FISH-150901-6607/publications"
        then the content should contain "shha<tbx392>"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "PMID:9007258"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/zfin.ttl"

## Genotype to Variant associations

    Scenario: User fetches genotype to publication associations
        Given a path "/bioentity/genotype/dbSNPIndividual:20985/variants"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "OMIM:608666.0003"
        then the JSON should have some JSONPath "associations[*].provided_by" containing "string" "https://data.monarchinitiative.org/ttl/coriell.ttl"
