# Biolink API

An API providing access to information on biologically and
biomedically relevant entities, and the relationships between them, including:

 * genes, gene products, proteins
 * diseases, phenotypes, traits and clinical measurements
 * pathways, biological process
 * substances: small molecules, drugs, chemical entities
 * biological and molecular roles and activities
 * genotypes, alleles, sequence variants; for plants, germplasms
 * environmental contexts and exposures
 * individual organisms: patients, cohorts, model organisms
 * cell lines and cell types
 * investigations: experiments, clinical trials and 'natural experiments'
 * genomic features
 * phylogenies
 * metadata: publications, ontology terms, database metadata, prefixes

This repository provides an example server for the biolink API. The
swagger is also generated from this.

## Demo

This API is designed to be implemented or partially implemented via a
variety of databases.

The Monarch instance provides access to a wide variety of aggregated
data:

http://api.monarchinitiative.org/api/

## Datamodel

See the swagger UI for more details. Click on 'model' under any of the routes.

The primary abstraction used in the modeling is the distinction
between _named objects_ and _associations_.

 * Named objects include things like genes, drugs, pathways.
    * specific types subclass from a more generic type
 * Associations connect these, usually via some _evidence_ and provenance information.
    * Some associations can be direct, others are indirect or *inferred*
    * Where associations are inferred, these is a *graph of evidence* tracing the primary associations

## Examples

See [EXAMPLE-QUERIES.md](EXAMPLE-QUERIES.md)

These examples are compiled from the [behave tests](tests/)

## Writing client code

The API uses Swagger, which means you can take advantage of a variety of swagger tooling

For example, to generate a python client:

    swagger-codegen generate -i http://api.monarchinitiative.org/api/swagger.json -l $* -o $@

# Contributing to BioLink-API

This is the repo:

https://github.com/monarch-initiative/biolink-api/

You can run a server instance locally with very little effort (less
than one minute), see below:

## Setting up

```
pyvenv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.:$PYTHONPATH
python biolink/app.py
```

to run:

```
python biolink/app.py
```

Then look at:

http://localhost:5000/api/

For the swagger docs

Note that only a small subset has been implemented

## Organization

This repo contains multiple sub-packages. These can all be used in
python programs independent of biolink or a web service context.

 * [biolink](biolink) FlaskREST service implementation for BioLink API
 * [biomodel](biomodel) Data access objects
 * [biogolr](biogolr) Python API onto Monarch and GO golr instances
 * [scigraph](scigraph) Python API onto Monarch SciGraph instance
 * [prefixcommons](prefixcommons) Python code for working with ID prefixes

## Goals

This API will wrap and integrate number of different more modular APIs
and database engines or analysis services. The idea is that the API
implementation will do the right thing - for example, using Solr for
searches but injecting results with fast in-memory traversal of
ontology graphs.

This is a proof of concept implementation. May be implemented using a JVM language, e.g. scala in future.



### Example API calls (OLD)

All assocations, first 10:

http://localhost:5000/api/link/search/

All mouse gene-phenotype associations:

http://localhost:5000/api/link/search/gene/phenotype/?map_identifiers=MGI&subject_taxon=NCBITaxon:10090

Same but with IDs mapped from NCBIGene to MGI (see #5):

http://localhost:5000/api/link/search/gene/phenotype/?subject_taxon=NCBITaxon:10090

phenotypes for a given gene

http://localhost:5000/api/bio/gene/ZFIN:ZDB-GENE-050417-357/phenotypes/

GO terms for a given gene (uses GO golr)

http://localhost:5000/api/bio/gene/ZFIN:ZDB-GENE-050417-357/function/

Query association by ID:

http://localhost:5000/api/link/cfef92b7-bfa3-44c2-a537-579078d2de37

Evidence graph as bbop-graph:

http://localhost:5000/api/evidence/graph/cfef92b7-bfa3-44c2-a537-579078d2de37

Evidence graph as image:

http://localhost:5000/api/evidence/graph/cfef92b7-bfa3-44c2-a537-579078d2de37/image

Anatomical entities for a given phenotype:

http://localhost:5000/api/bioentity/phenotype/ZP:0004204/anatomy/

## Implementation and Project Organization

This is intended as a think wrapper layer, integrating existing
services, as shown here:

![img](docs/biolink-integrator-arch.png)

This is only very partially integrated

We have some business logic in the following sub-packages:

 * [scigraph](scigraph) - python API for Monarch Neo4J instance and generic SciGraph functions
 * [biogolr](biogolr) - python API for any golr instance (GO or Monarch)
 * [obographs](obographs) - python ontology object model and utilities. See [obographs](https://github.com/geneontology/obographs)
 * [causalmodels](causalmodels) - python API for LEGO, and wrapper to GO triplestore
 * [prefixcommons](prefixcommons) - python utilities for handling prefixes/CURIEs


These may eventually migrate to their own repos, see #16

### Solr indices

Most of the `link` subset is implemented via the Monarch Golr, with
function queries coming from the GO instance. See:

https://github.com/monarch-initiative/biolink-api/issues/14

### SciGraph

Two different ways of accessing this are used:

 * Direct access via BOLT/Cypher
 * Access to SciGraph API layer

### Triplestore

The `lego` calls are imlemented as calls to the GO triplestore.

### OwlSim

http://owlsim3.monarchinitiative.org/api/docs/

## Notes

   
