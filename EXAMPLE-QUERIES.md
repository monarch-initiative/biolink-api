This is a marked up version of the executable behave tests in the [tests](tests/) directory

# Association queries

## General Associations

Path: `/association/find/`

Note that inference is on by default. Queries for a general taxonomic class will find associations to subclass.

Scenario: __Client queries for all annotations in Monotremes (e.g. Duck billed platypus)__

URL: [http://api.monarchinitiative.org/api/association/find/?subject_taxon=NCBITaxon:9255&rows=10&fl_excludes_evidence=true&page=1](http://api.monarchinitiative.org/api/association/find/?subject_taxon=NCBITaxon:9255&rows=10&fl_excludes_evidence=true&page=1)


when the content is converted to JSON:

 * then the JSON should have some JSONPath `associations[*].subject.taxon.label` with `string` `Ornithorhynchus anatinus`
    * and the JSON should have some JSONPath `associations[*].object.label` with `string` `Asthma`

# Association queries work as expected

## Gene-Phenotype Associations

Scenario: __User queries for mouse genes with abnormal Bowman membrane phenotype__

URL: [http://api.monarchinitiative.org/api/association/find/gene/phenotype/?subject_taxon=NCBITaxon:10090&rows=10&object=MP:0008521](http://api.monarchinitiative.org/api/association/find/gene/phenotype/?subject_taxon=NCBITaxon:10090&rows=10&object=MP:0008521)

 * then the content should contain "abnormal Bowman membrane"

when the content is converted to JSON:

 * then the JSON should have some JSONPath `associations[*].subject.id` with `string` `MGI:1342287`
    * and the JSON should have some JSONPath `associations[*].object.id` with `string` `MP:0008521`
    * and the JSON should have some JSONPath `associations[*].object.label` with `string` `abnormal Bowman membrane`

# Association queries return lists of associations

## Phenotype Associations

Scenario: __Client wants human and mouse genes with eyelid abnormalities, using a HPO ID__

URL: [http://api.monarchinitiative.org/api/association/find/gene/phenotype?subject_taxon=NCBITaxon:40674&object=HP:0000492&fl_excludes_evidence=true&page=1](http://api.monarchinitiative.org/api/association/find/gene/phenotype?subject_taxon=NCBITaxon:40674&object=HP:0000492&fl_excludes_evidence=true&page=1)


when the content is converted to JSON:

####      then the JSON should have some JSONPath `associations[*].object.id` with `string` `HP:0011025`

Scenario: __Client wants human and mouse genes with cardiovascular phenotypes, using an MP ID__

URL: [http://api.monarchinitiative.org/api/association/find/gene/phenotype?subject_taxon=NCBITaxon:40674&object=MP:0001340&fl_excludes_evidence=true&page=1](http://api.monarchinitiative.org/api/association/find/gene/phenotype?subject_taxon=NCBITaxon:40674&object=MP:0001340&fl_excludes_evidence=true&page=1)


when the content is converted to JSON:


# Disease entity queries work as expected

TODO - consider swapping subject/object

## Diseases

Scenario: __User queries for a specific form of Parkinson disease__

URL: [http://api.monarchinitiative.org/api/bioentity/disease/OMIM:605543/models](http://api.monarchinitiative.org/api/bioentity/disease/OMIM:605543/models)

 * then the content should contain "Snca"
    * and the content should contain "Mus musculus"
    * and the content should contain "C57BL/6"

when the content is converted to JSON:

 * then the JSON should have some JSONPath `associations[*].subject.id` with `string` `MGI:5544308`

Scenario: __User queries for worm models of supranuclear palsy__

URL: [http://api.monarchinitiative.org/api/bioentity/disease/DOID:678/models/NCBITaxon:6239](http://api.monarchinitiative.org/api/bioentity/disease/DOID:678/models/NCBITaxon:6239)

 * then the content should contain "wormbase"
    * and the content should contain "Caenorhabditis elegans"
    * and the content should contain "ptl-1"

Scenario: __User queries for dog models of lipid storage diseases (e.g. gangliosidosis)__

URL: [http://api.monarchinitiative.org/api/bioentity/disease/DOID:9455/models/NCBITaxon:9615](http://api.monarchinitiative.org/api/bioentity/disease/DOID:9455/models/NCBITaxon:9615)

 * then the content should contain "GM11474"
    * and the content should contain "Canis lupus"
    * and the content should contain "Gangliosidosis"


# bioentity routes work as expected

These routes (`bioentity`) provide a way to query for domain-specific
objects such as genes, diseases, etc, as well as for associations
between these entities

## Genes
 
Scenario: __User fetches all information on a human gene__

URL: [http://api.monarchinitiative.org/api/bioentity/gene/NCBIGene:84570](http://api.monarchinitiative.org/api/bioentity/gene/NCBIGene:84570)

 * then the content should contain "COL25A1"

when the content is converted to JSON:

 * then the JSON should have the top-level property "id"
    * and the JSON should have a JSONPath `homology_associations[*].object`
    * and the JSON should have a JSONPath `homology_associations[*].object.id`
    * and the JSON should have some JSONPath `homology_associations[*].object.label` with `string` `col25a1`

Scenario: __User fetches all information on a mouse gene__

URL: [http://api.monarchinitiative.org/api/bioentity/gene/MGI:1342287](http://api.monarchinitiative.org/api/bioentity/gene/MGI:1342287)

 * then the content should contain "Klf4"

when the content is converted to JSON:

 * then the JSON should have the top-level property "id"
    * and the JSON should have some JSONPath `phenotype_associations[*].object.id` with `string` `MP:0008521`
    * and the JSON should have some JSONPath `phenotype_associations[*].object.label` with `string` `abnormal Bowman membrane`

### TODO ensure label populated in scigraph call

Scenario: __User fetches all information on the same mouse gene, using an ENSEMBL ID__

URL: [http://api.monarchinitiative.org/api/bioentity/gene/ENSEMBL:ENSMUSG00000003032](http://api.monarchinitiative.org/api/bioentity/gene/ENSEMBL:ENSMUSG00000003032)

 * then the content should contain "Klf4"

when the content is converted to JSON:

 * then the JSON should have some JSONPath `phenotype_associations[*].subject.id` with `string` `MGI:1342287`
    * and the JSON should have some JSONPath `phenotype_associations[*].object.id` with `string` `MP:0008521`
    * and the JSON should have some JSONPath `phenotype_associations[*].object.label` with `string` `abnormal Bowman membrane`

Scenario: __User fetches all phenotypes for a mouse gene__

URL: [http://api.monarchinitiative.org/api/bioentity/gene/MGI:1342287/phenotypes](http://api.monarchinitiative.org/api/bioentity/gene/MGI:1342287/phenotypes)


when the content is converted to JSON:

 * then the JSON should have some JSONPath `associations[*].object.id` with `string` `MP:0008521`
    * and the JSON should have some JSONPath `associations[*].object.label` with `string` `abnormal Bowman membrane`

Scenario: __User fetches all GO functional assignments for a zebrafish gene__

URL: [http://api.monarchinitiative.org/api/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function](http://api.monarchinitiative.org/api/bioentity/gene/ZFIN:ZDB-GENE-050417-357/function)


when the content is converted to JSON:

 * then the JSON should have some JSONPath `associations[*].object.id` with `string` `GO:0030500`
    * and the JSON should have some JSONPath `associations[*].object.label` with `string` `regulation of bone mineralization`

Scenario: __User fetches all interactions for a mouse gene__

URL: [http://api.monarchinitiative.org/api/bioentity/gene/MGI:1342287/interactions](http://api.monarchinitiative.org/api/bioentity/gene/MGI:1342287/interactions)

 * then the content should contain "http://data.monarchinitiative.org/ttl/biogrid.ttl"

when the content is converted to JSON:

 * then the JSON should have some JSONPath `associations[*].object.id` with `string` `MGI:88039`
    * and the JSON should have some JSONPath `associations[*].object.label` with `string` `Apc`


# Phenotype entity queries work as expected

TODO

## Phenotypes

Scenario: __User queries for mouse genes with abnormal Bowman membrane phenotype__

URL: [http://api.monarchinitiative.org/api/bioentity/phenotype/MP:0008521](http://api.monarchinitiative.org/api/bioentity/phenotype/MP:0008521)

 * then the content should contain "foo"

### Phenotype connections

Scenario: __Client requires mapping between enlarged thymus (MP) and anatomy__

URL: [http://api.monarchinitiative.org/api/bioentity/phenotype/MP:0000709/anatomy](http://api.monarchinitiative.org/api/bioentity/phenotype/MP:0000709/anatomy)

 * then the content should contain "thymus"
    * and the content should contain "UBERON:0002370"

Scenario: __Client requires mapping between prominent nose (HP) and anatomy__

URL: [http://api.monarchinitiative.org/api/bioentity/phenotype/HP:0000448/anatomy](http://api.monarchinitiative.org/api/bioentity/phenotype/HP:0000448/anatomy)

 * then the content should contain "nose"
    * and the content should contain "UBERON:0000004"

Scenario: __Client requires mapping between phenotype (ZP) and anatomy__

URL: [http://api.monarchinitiative.org/api/bioentity/phenotype/ZP:0004204/anatomy](http://api.monarchinitiative.org/api/bioentity/phenotype/ZP:0004204/anatomy)

 * then the content should contain "muscle pioneer"
    * and the content should contain "ZFA:0001086"



# substance routes work as expected

## Substance
 
Scenario: __User requests processes or pathways associated with amitrole__

URL: [http://api.monarchinitiative.org/api/bioentity/substance/CHEBI:40036/participant_in/](http://api.monarchinitiative.org/api/bioentity/substance/CHEBI:40036/participant_in/)

 * then the content should contain "aminotriazole transporter activity"



# Expansion and contraction of URIs

## List all prefixes

Scenario: __Client code requires list of all prefixes in use__

URL: [http://api.monarchinitiative.org/api/identifier/prefixes](http://api.monarchinitiative.org/api/identifier/prefixes)

 * then the content should contain "UBERON"

### Phenotype connections

Scenario: __Contract a GO URI to a GO OBO-style ID__

URL: [http://api.monarchinitiative.org/api/identifier/prefixes/contract/http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FGO_0008150](http://api.monarchinitiative.org/api/identifier/prefixes/contract/http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FGO_0008150)

 * then the content should contain "GO:0008150"

Scenario: __Expand a GO ID to a URI__

URL: [http://api.monarchinitiative.org/api/identifier/prefixes/expand/GO:0008150](http://api.monarchinitiative.org/api/identifier/prefixes/expand/GO:0008150)

 * then the content should contain "http://purl.obolibrary.org/obo/GO_0008150"


# Dynamic information content calculation

Scenario: __Client code fetches ICs for MP terms based on mouse gene associations__

URL: [http://api.monarchinitiative.org/api/information_content/gene/phenotype/NCBITaxon:9606](http://api.monarchinitiative.org/api/information_content/gene/phenotype/NCBITaxon:9606)

 * then the content should contain "MP:0000709"



