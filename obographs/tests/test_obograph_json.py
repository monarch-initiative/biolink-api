from biomodel.obograph import *
from obographs.obograph_util import *
from obographs.cgraph import *
from obographs.graph_io import *
import json

f = open('obographs/tests/nucleus.json', 'r')
jsonstr = f.read()
f.close()
jobj = json.loads(jsonstr)

g = convert_json_object(jobj)
show_tree(g, None)
