Feature: Case association queries that return a list of associations

## Case to disease associations

    Scenario: Search for diseases associated with a case
        Given a path "/bioentity/case/BNODE:person-51-1/diseases"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "affected female proband with Mucopolysaccharidosis type vi"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MONDO:0009661"

## Case to genotype associations

    Scenario: Search for genotypes associated with a case
        Given a path "/bioentity/case/BNODE:person-GM21698/genotypes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "BNODE:genoGM21698"

## Case to model associations

    Scenario: Search for models associated with a case
        Given a path "/bioentity/case/BNODE:person-SL5-2/models"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "Coriell:HG03064"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "derives_from"

## Case to phenotype associations
# TODO

## Case to variant associations

    Scenario: Search for variants associated with a case
        Given a path "/bioentity/case/BNODE:person-GM00005/variants"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "some karyotype alteration on chr14"
