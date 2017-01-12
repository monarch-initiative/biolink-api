Feature: Expansion and contraction of URIs

## List all prefixes

 Scenario: Client code requires list of all prefixes in use
    Given a path "/identifier/prefixes"
     then the content should contain "UBERON"

### Phenotype connections

 Scenario: Contract a GO URI to a GO OBO-style ID
    Given a path "/identifier/prefixes/contract/http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FGO_0008150"
     then the content should contain "GO:0008150"

 Scenario: Expand a GO ID to a URI
    Given a path "/identifier/prefixes/expand/GO:0008150"
     then the content should contain "http://purl.obolibrary.org/obo/GO_0008150"

