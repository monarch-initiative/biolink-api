Feature: substance routes work as expected

## Get associations between a given drug and an activity
 
 Scenario: User requests processes or pathways associated with amitrole
    Given a path "/bioentity/substance/CHEBI:40036/participant_in/"
     then the content should contain "aminotriazole transmembrane transporter activity"

## Get associations between a given drug and roles

 Scenario: User requests for roles that amitrole plays
    Given a path "/bioentity/substance/CHEBI:40036/roles/"
     then the content should contain "herbicide"
     then the content should contain "carotenoid biosynthesis inhibitor"


## Get associations between a given drug and a disease that it treats

# TODO