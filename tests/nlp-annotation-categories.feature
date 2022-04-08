Feature: NLP Annotate Entities returns categories from SciGraph

## NLP Annotate Entities returns results w/non-empty 'categories'

   Scenario: User requests NLP annotated entities for the string 'males'
      Given a path "/nlp/annotate/entities?content=males"
      then the JSON should have some JSONPath "spans.[*].token.[*].categories.[*]" containing "string" "anatomical entity"
