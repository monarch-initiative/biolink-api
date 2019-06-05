
Feature: slimmer routes work as expected

## Map2slim for GO with MGI
 
 Scenario: User maps annotation for an MGI gene to a slim
    Given a path "/bioentityset/slimmer/function?slim=GO:0003824&slim=&GO:0004872&slim=GO:0005102&slim=GO:0005215&slim=GO:0005198&slim=GO:0008092&slim=GO:0003677&slim=GO:0003723&slim=GO:0001071&slim=GO:0036094&slim=GO:0046872&slim=GO:0030246&slim=GO:0008283&slim=GO:0071840&slim=GO:0051179&slim=GO:0032502&slim=GO:0000003&slim=GO:0002376&slim=GO:0050877&slim=GO:0050896&slim=GO:0023052&slim=GO:0010467&slim=GO:0019538&slim=GO:0006259&slim=GO:0044281&slim=GO:0050789&slim=GO:0005576&slim=GO:0005829&slim=GO:0005856&slim=GO:0005739&slim=GO:0005634&slim=GO:0005694&slim=GO:0016020&slim=GO:0071944&slim=GO:0030054&slim=GO:0042995&slim=GO:0032991&subject=MGI:98371"
     then the content should contain "Sox9"
    when the content is converted to JSON
      then the JSON should have some JSONPath "[*].assocs[*].subject.id" with "string" "MGI:98371"
      then the JSON should have some JSONPath "[*].assocs[*].subject.label" with "string" "Sox9"
      and the JSON should have some JSONPath "[*].slim" with "string" "GO:0010467"

## Slimmer anatomy

## Slimmer phenotype
