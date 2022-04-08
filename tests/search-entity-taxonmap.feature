Feature: Search Entity Term returns a _taxon_map key w/taxon IDs

## Search Entity Term returns a _taxon_map key

   Scenario: User queries for marfan's disease
      Given a path "/search/entity/marfan"
      then the content should contain "_taxon_map"
      then the JSON should have some JSONPath "facet_counts._taxon_map.[*].id" containing "string" "NCBITaxon:9606"
      then the JSON should have some JSONPath "facet_counts._taxon_map.[*].label" containing "string" "Homo sapiens"
