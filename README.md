# Python API for SciGraph

For details on SciGraph, see [SciGraph](https://github.com/SciGraph/SciGraph/)

This provides two means of access:

 * via BOLT
 * via the SciGraph REST API

Note that this code originally lived here: https://github.com/SciGraph/py-SciGraph

## Python Examples

### Neighbour Query

```
from scigraph.api.SciGraph import SciGraph

sg = SciGraph("http://datagraph.monarchitiative.org/")
g = sg.neighbors('OMIM:118300',{'depth':1})
for n in g.nodes:
  print(n.id +" " + n.label)
for e in g.edges:
  print(n.subject +" " + e.predicate + " " + e.target)
```
    
## Command Line Examples

For up to date help, always use:

    ./run-scigr.py -h

The most useful global parameter is `-u` which sets the base URL

### Autocomplete

    ./run-scigr.py  a Parkinson

### Search

    ./run-scigr.py  s Parkinson

### Annotation

    ./run-scigr.py ann "the big ears and the hippocampus neurons"

### Neighbors

    ./run-scigr.py -t tsv  n OMIM:118300

### Graph Visualization

    ./run-scigr.py -t png  g OMIM:118300


