Feature: Variant association queries that return a list of associations

## Variant to Case associations

    Scenario: User queries for cases associated with a variant
        Given a path "/bioentity/variant/dbSNP:rs766529116/cases"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" ":MONARCH:c000017"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "case"

## Variant to Disease associations

    Scenario: User queries for diseases associated with a variant
        Given a path "/bioentity/variant/ClinVarVariant:14925/diseases"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "HSPG2, 9-BP DEL"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MONDO:0009717"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "disease"

## Variant to Gene associations

    Scenario: User queries for genes associated with a variant
        Given a path "/bioentity/variant/ClinVarVariant:39783/genes"
        then the JSON should have some JSONPath "associations[*].subject.label" containing "string" "Gly34Val"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "HGNC:10896"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "gene"

## Variant to Genotype associations

    Scenario: User queries for genotypes associated with a variant
        Given a path "/bioentity/variant/ZFIN:ZDB-ALT-010427-8/genotypes"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "tbx392"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "ZFIN:ZDB-FISH-150901-24810"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "genotype"

## Variant to Model associations

    Scenario: User queries for models associated with a variant
        Given a path "/bioentity/variant/dbSNP:rs5030868/models"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "rs5030868-A"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "Coriell:GM01165"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "model"

## Variant to Phenotype associations
    # https://github.com/monarch-initiative/monarch-ui/issues/189
    # TODO replace with gwas catalog association
    #Scenario: User queries for phenotypes associated with a variant
    #    Given a path "/bioentity/variant/ClinVarVariant:39783/phenotypes"
    #   then the JSON should have some JSONPath "associations[*].subject.label" containing "string" "p.Gly34Val"
    #    then the JSON should have some JSONPath "associations[*].object.label" with "string" "Craniosynostosis"
    #    then the JSON should have some JSONPath "associations[*].object.category" containing "string" "phenotype"

## Variant to Publication associations

    Scenario: User queries for publications associated with a variant
        Given a path "/bioentity/variant/ClinVarVariant:39783/publications"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "PMID:23103230"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "publication"
