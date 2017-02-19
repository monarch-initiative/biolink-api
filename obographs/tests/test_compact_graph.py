from biomodel.obograph import *
from obographs.obograph_util import *
from obographs.cgraph import *
import json

f = open('obographs/tests/nucleus.json', 'r')
jsonstr = f.read()
f.close()
jobj = json.loads(jsonstr)

gd = GraphDocument.from_json(jobj)
g = gd.graphs[0]
cg = CompactGraph(nodes=g.nodes, edges=g.edges)
cg.serialize()
