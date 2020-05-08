Feature: Case association queries that return a list of associations

## Case to disease associations

    Scenario: Search for diseases associated with a case
        Given a path "/bioentity/case/:MONARCH:c000017/phenotypes"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "HP:0004488"


## Case to phenotype associations
# TODO

## Case to variant associations

    Scenario: Search for variants associated with a case
        Given a path "/bioentity/case/:MONARCH:c000017/variants"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "dbSNP:rs766529116"
