Feature: Lexical Searches work as expected

## Disease Search by Label

 Scenario: User queries diseases matching Fanconi Anemia
    Given a path "/search/entity/Fanconi?category=disease&rows=20"
     then the content should contain "Fanconi anemia"
    when the content is converted to JSON
      then the JSON should have some JSONPath "docs[*].id" with "string" "DOID:13636"
