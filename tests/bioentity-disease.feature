Feature: Disease entity queries work as expected

## Disease to Model associations

    Scenario: User queries for a specific form of episodic ataxia disease
        Given a path "/bioentity/disease/OMIM:160120/models"
        then the content should contain "Kcna1"
        and the content should contain "Mus musculus"
        when the content is converted to JSON
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "MGI:2655686"

    Scenario: User queries for worm models of supranuclear palsy
        Given a path "/bioentity/disease/DOID:678/models?taxon=NCBITaxon:6237"
        then the content should contain "wormbase"
        and the content should contain "Caenorhabditis"
        and the content should contain "ptl-1"

    Scenario: User queries for worm models of lipid storage diseases (e.g. gangliosidosis)
        Given a path "/bioentity/disease/DOID:9455/models?taxon=NCBITaxon:6237"
        then the content should contain "wormbase"
        and the content should contain "Caenorhabditis"
        and the content should contain "lipl-1"

    Scenario: User queries for Parkinson disease, late-onset and can see onset and inheritance
        Given a path "/bioentity/disease/MONDO:0008199"
        when the content is converted to JSON
        then the JSON should have some JSONPath "clinical_modifiers[*].id" with "string" "HP:0003676"
        then the JSON should have some JSONPath "clinical_modifiers[*].label" with "string" "Progressive"
        then the JSON should have some JSONPath "inheritance[*].id" with "string" "HP:0003745"
        then the JSON should have some JSONPath "inheritance[*].label" with "string" "Sporadic"

## Disease to Gene associations

    Scenario: User queries for genes associated with lipid storage diseases (e.g. gangliosidosis)
        Given a path "/bioentity/disease/DOID:9455/genes?rows=0&fetch_objects=true&facet=true"
        then the content should contain "HGNC:14537"

## Disease to Gene causal associations

    Scenario: User queries for causal genes associated with Marfan Syndrome
        Given a path "/bioentity/disease/MONDO:0007947/genes?rows=10&association_type=causal"
        then the JSON should have some JSONPath "associations[0].object.label" with "string" "FBN1"
        then the JSON should have some JSONPath "numFound" with "integer" "1"

## Disease to Gene non causal associations

    Scenario: User queries for non causal genes associated with Marfan Syndrome
        Given a path "/bioentity/disease/MONDO:0007947/genes?rows=10&association_type=non_causal"
        then the JSON should not have some JSONPath "associations[*].object.label" with "string" "FBN1"

## Disease to Gene all associations

    Scenario: User queries for all genes associated with Marfan Syndrome
        Given a path "/bioentity/disease/MONDO:0007947/genes?rows=10"
        then the JSON should have some JSONPath "associations[*].object.label" with "string" "FBN1"

## Disease to Phenotype associations

    Scenario: User queries for phenotypes associated with a disease
        Given a path "/bioentity/disease/OMIM:605543/phenotypes"
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MONDO:0011562"
        then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "disease"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "HP:0001300"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "phenotype"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "has phenotype"

## Disease to Genotype associations

    Scenario: User queries for genotypes associated with a disease
        Given a path "/bioentity/disease/MONDO:0007243/genotypes"
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MONDO:0007243"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Burkitt lymphoma"
        then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "disease"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "dbSNPIndividual:10748"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "genotype"

## Disease to Variant associations

    Scenario: User queries for variants associated with a disease
        Given a path "/bioentity/disease/MONDO:0007243/variants"
        then the JSON should have some JSONPath "associations[*].subject.id" with "string" "MONDO:0007243"
        then the JSON should have some JSONPath "associations[*].subject.label" with "string" "Burkitt lymphoma"
        then the JSON should have some JSONPath "associations[*].subject.category" containing "string" "disease"
        then the JSON should have some JSONPath "associations[*].object.id" with "string" "ClinVarVariant:12577"
        then the JSON should have some JSONPath "associations[*].object.category" containing "string" "variant"
        then the JSON should have some JSONPath "associations[*].relation.label" with "string" "pathogenic_for_condition"