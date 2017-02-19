# obographs - a python API for working with ontology graphs

NOTE: This is a standalone module currently in the biolink-api
repo. It does not depend on any other module in this repo (other than
prefixcommons), and will be moved to its own repo.

This module maps ontologies to networkx MultiDiGraphs, and provides useful
convenience methods over these.

There are two ways of initiating a networkx graph:

 * via an obo-json file
 * via remote query to a SPARQL service (currently  ontobee)

## Working with JSON files

See https://github.com/geneontology/obographs

## Working with a remote SPARQL service

 * the first time an ontology is referenced, basic axioms will be fetched via SPARQL
 * these will be cached in `/tmp/.cache/`
 * the second time the same ontology is referenced, the disk cache will be used
 * if an ontology is referenced a second time in the same in-memory session, the disk cache is bypassed and in-memory (lru) cache is used



## Command Line Usage

```
export PATH $HOME/repos/bioink-api/obographs/bin
ogr -h
```

Note you need to be connected to a network

### Ancestors queries


List all ancestors:

```
./obographs/bin/ogr.py -r cl a neuron
```

Shows ancestors as tree, following only subclass

```
./obographs/bin/ogr.py -r cl -p subClassOf -t tree a neuron
```

Descendants of neuron, parts and subtypes

```
./obographs/bin/ogr.py -r cl -p subClassOf -p BFO:0000050 -t tree a neuron
```

### Visualization using obographviz

Requires js lib:

```
ogr -p subClassOf BFO:0000050 -r go -t png   a nucleus
```

This proceeds by:

 1. Using the python obographs library to extract a networkx subgraph around the specified node
 2. Write as obographs-json
 3. Calls og2dot.js
