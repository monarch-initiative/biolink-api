"""
Ontology graph manager - abstracts from details of how to fetch remote ontologies.

 - from a remote SPARQL endpoint
    - defaults to ontobee (TODO: configurable)
 - from local filesystem (obojson format)
 - from an OBO PURL
    - launches owltools in subprocess to convert OWL to JSON

Implements various levels of caching

"""

from obographs.graph_io import *
import networkx as nx
from networkx.algorithms.dag import ancestors, descendants
from networkx.drawing.nx_pydot import write_dot
from prefixcommons.curie_util import expand_uri
import obographs.obograph_util as obograph_util
import logging
import os
import subprocess
from cachier import cachier
import datetime

SHELF_LIFE = datetime.timedelta(days=3)

@cachier(stale_after=SHELF_LIFE)
def retrieve_ontology(ont):
    """
    Create a networkx graph
    """
    g = None
    logging.info("Determining strategy to load '{}' into memory...".format(ont))
    if ont.find(".") > 0 and os.path.isfile(ont):
        logging.info("Fetching obograph-json file from filesystem")
        g = obograph_util.convert_json_file(ont)
    elif ont.startswith("obo:"):
        logging.info("Fetching from OBO PURL")
        if ont.find(".") == -1:
            ont += '.owl'
        fn = '/tmp/'+ont
        if not os.path.isfile(fn):
            url = ont.replace("obo:","http://purl.obolibrary.org/obo/")
            cmd = ['owltools',url,'-o','-f','json',fn]
            cp = subprocess.run(cmd, check=True)
            logging.info(cp)
        else:
            logging.info("using cached file: "+fn)
        g = obograph_util.convert_json_file(fn)
    else:
        logging.info("Fetching from SPARQL")        
        g = get_digraph(ont, None, True)
    return g

def retrieve_filtered_graph(ont, predicates=None):
    """
    Create a networkx graph, removing unwanted edges
    """
    srcg = retrieve_graph(ont)
    if predicates is None:
        logging.info("No filtering on "+ont)
        return srcg
    logging.info("Filtering {} for {}".format(ont, predicates))
    g = networkx.MultiDiGraph()
    
    logging.info("copying nodes")
    for n,d in srcg.nodes_iter(data=True):
        g.add_node(n, attr_dict=d)

    logging.info("copying edges")
    num_edges = 0
    for x,y,d in srcg.edges_iter(data=True):
        if d['pred'] in predicates:
            num_edges += 1
            g.add_edge(x,y,attr_dict=d)
    logging.info("Filtered edges: {}".format(num_edges))
    return g
