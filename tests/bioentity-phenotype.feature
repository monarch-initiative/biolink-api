Feature: Phenotype entity queries work as expected

TODO

## Phenotypes

 Scenario: User queries for mouse genes with abnormal Bowman membrane phenotype
    Given a path "/bioentity/phenotype/MP:0008521"
     then the content should contain "foo"

 Scenario: Client requires mapping between abnormal Bowman membrane phenotype (MP) and anatomy
    Given a path "/bioentity/phenotype/MP:0008521/anatomy"
     then the content should contain "cornea"
    when the content is converted to JSON
     then the JSON should have some JSONPath "id" with "string" "UBERON:0004370"
     and the JSON should have some JSONPath "id" with "string" "anterior limiting lamina of cornea"

 Scenario: Client requires mapping between phenotype (ZP) and anatomy
    Given a path "/bioentity/phenotype/ZP:0004204/anatomy"
     then the content should contain "cornea"
    when the content is converted to JSON
     then the JSON should have some JSONPath "id" with "string" "UBERON:0004370"
     and the JSON should have some JSONPath "id" with "string" "anterior limiting lamina of cornea"

