Feature: Phenotype entity queries work as expected

TODO

## Phenotypes

 Scenario: User queries for mouse genes with abnormal Bowman membrane phenotype
    Given a path "/bioentity/phenotype/MP:0008521"
     then the content should contain "foo"

### Phenotype connections

 Scenario: Client requires mapping between enlarged thymus (MP) and anatomy
    Given a path "/bioentity/phenotype/MP:0000709/anatomy"
     then the content should contain "thymus"
      and the content should contain "UBERON:0002370"

 Scenario: Client requires mapping between prominent nose (HP) and anatomy
    Given a path "/bioentity/phenotype/HP:0000448/anatomy"
     then the content should contain "nose"
      and the content should contain "UBERON:0000004"

 Scenario: Client requires mapping between phenotype (ZP) and anatomy
    Given a path "/bioentity/phenotype/ZP:0004204/anatomy"
     then the content should contain "muscle pioneer"
      and the content should contain "ZFA:0001086"

