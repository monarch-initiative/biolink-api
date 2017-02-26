# obographs - a python API for working with ontology graphs

NOTE: This is a standalone module currently in the biolink-api
repo. It does not depend on any other module in this repo (other than
prefixcommons), and will be moved to its own repo.

This module maps (local or remote) ontologies to networkx
MultiDiGraphs, and provides useful convenience methods over these,
including display as graphs and trees.

There are two ways of initiating a networkx graph:

 * via a local obo-json file
 * via remote connections to OBO PURLs
 * via remote query to a SPARQL service (currently  ontobee, but soon others)

Persistent caching is used (currently cachier) to avoid repeated expensive I/O connections

This is handled via the graph_manager.py module

# Command Line Usage

## Initial Setup

```
export PATH $HOME/repos/bioink-api/obographs/bin
ogr -h
```

Note you need to be connected to a network

Note: command line interface may change

## Connecting to ontologies

Specify an ontology with the `-r` option. this will always be the OBO name, for example `go`, `cl`, `mp`, etc

 * `-r go` connect to GO via default method (currently SPARQL)
 * `-r obo:go` connect to GO via download and cache of ontology from PURL
 * `-r /users/my/my-ontologies/go.json` use local download of ontology

In the following we assume default method, but can be substituted.

## Ancestors queries

List all ancestors:

```
ogr -r cl neuron
```

Show ancestors as tree, following only subclass:

```
ogr -r cl -p subClassOf -t tree neuron
```

generates:

```
     % GO:0005623 ! cell
      % CL:0000003 ! native cell
       % CL:0000255 ! eukaryotic cell
        % CL:0000548 ! animal cell
         % CL:0002319 ! neural cell
          % CL:0000540 ! neuron * 
       % CL:0002371 ! somatic cell
        % CL:0002319 ! neural cell
         % CL:0000540 ! neuron * 
```

Descendants of neuron, parts and subtypes

```
ogr -r cl -p subClassOf -p BFO:0000050 -t tree -d d neuron
```

Descendants and ancestors of neuron, parts and subtypes

```
ogr -r cl -p subClassOf -p BFO:0000050 -t tree -d du neuron
```

## Visualization using obographviz

Requires: https://www.npmjs.com/package/obographviz

Add og2dot.js to path

```
ogr -p subClassOf BFO:0000050 -r go -t png   a nucleus
```

This proceeds by:

 1. Using the python obographs library to extract a networkx subgraph around the specified node
 2. Write as obographs-json
 3. Calls og2dot.js

Output:

![img](https://github.com/biolink/biolink-api/raw/master/obographs/docs/nucleus.png)

## Search

List exact matches to neuron

```
ogr -r cl neuron
```

Terms starting with neuron, SQL style

```
ogr -r cl neuron%
```

Terms starting with neuron, regex (equivalent to above)

```
ogr -r cl -s r ^neuron
```

Terms ending with neuron

```
ogr -r cl -s r neuron$
```

Terms containing the string neuron

```
ogr -r cl -s r neuron
```

Note: any of the above can be fed into other renderers, e.g. trees, graphs

