Feature: negation field works in payload

## Negation

Scenario: User fetches GO functional assignments and wishes to filter negated results
    Given a path "/bioentity/gene/MGI:1332638/function?rows=100"
    when the content is converted to JSON
      then the JSON should have some JSONPath "associations[*].object.id" with "string" "GO:0005730"
      and the JSON should have some JSONPath "associations[*].qualifiers" containing "string" "not"
      and the JSON should have some JSONPath "associations[*].negated" with "boolean" "true"
