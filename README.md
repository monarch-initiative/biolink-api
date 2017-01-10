# Biolink API

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

## Goals

This API will wrap and integrate number of different more modular APIs
and database engines or analysis services. The idea is that the API
implementation will do the right thing - for example, using Solr for
searches but injecting results with fast in-memory traversal of
ontology graphs.

This is a proof of concept implementation. May be implemented using a JVM language, e.g. scala in future.

## Overview

The API is intended to be as self-explanatory as possible, via
swagger/openapi annotations. Please consult these (you will need to
start your own server)


### Example API calls

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

   
