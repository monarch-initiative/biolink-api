
Feature: substance routes work as expected

## Substance
 
 Scenario: User requests processes or pathways associated with amitrole
    Given a path "/bioentity/substance/CHEBI:40036/participant_in/"
     then the content should contain "aminotriazole transporter activity"


