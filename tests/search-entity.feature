Feature: Lexical Searches work as expected

## Disease Search by Label

 Scenario: User queries diseases matching Fanconi Anemia
    Given a path "/search/entity/Fanconi+anemia?category=disease&rows=20"
     then the content should contain "Fanconi anemia"
