Feature: Dynamic information content calculation

 Scenario: Client code fetches ICs for MP terms based on mouse gene associations
    Given a path "/ontol/information_content/gene/phenotype/NCBITaxon:9606"
     then the content should contain "MP:0000709"


