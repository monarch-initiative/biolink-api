#!/usr/bin/env python

"""
Command line wrapper to obographs library.

Type:

    ogr -h

For instructions

"""

import argparse
from obographs.sparql2ontology import *
from obographs.graph_io import *
import networkx as nx
from networkx.algorithms.dag import ancestors, descendants
from networkx.drawing.nx_pydot import write_dot
from prefixcommons.curie_util import expand_uri
import obographs.obograph_util as obograph_util
from obographs.graph_manager import retrieve_filtered_graph
from obographs.ontol_factory import OntologyFactory
import logging
import os
import subprocess

def main():
    """
    Wrapper for OGR
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("Welcome!")
    parser = argparse.ArgumentParser(description='Wrapper for obographs library'
                                                 """
                                                 By default, ontologies are cached locally and synced from a remote sparql endpoint
                                                 """,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--resource', type=str, required=False,
                        help='Name of ontology')
    parser.add_argument('-o', '--outfile', type=str, required=False,
                        help='Path to output file')
    parser.add_argument('-t', '--to', type=str, required=False,
                        help='Output to (tree, dot, ...)')
    parser.add_argument('-d', '--direction', type=str, default='u', required=False,
                        help='u = up, d = down, ud = up and down')
    parser.add_argument('-p', '--properties', nargs='*', type=str, required=False,
                        help='Properties')
    parser.add_argument('-c', '--container_properties', nargs='*', type=str, required=False,
                        help='Properties to nest in graph')

    args = parser.parse_args()
    handle = args.resource
    
    factory = OntologyFactory()
    ont = factory.create(handle)
    g = ont.get_filtered_graph(relations=args.properties)

    qids = []
    nodes = set()
    dirn = args.direction
    for id in resolve_ids(g, args.ids, args):
        qids.append(id)
        nodes.add(id)
        if dirn.find("u") > -1:
            nodes.update(ancestors(g,id))
        if dirn.find("d") > -1:
            nodes.update(descendants(g,id))
    show_subgraph(g, nodes, qids, args)

def cmd_descendants(handle, args):
    g = retrieve_filtered_graph(handle, predicates=args.properties)

    qids = []
    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        qids.append(id)
        nodes.update(descendants(g,id))
        nodes.add(id)
    show_subgraph(g, nodes, qids, args)

def cmd_graph(handle, args):
    g = retrieve_filtered_graph(handle, predicates=args.properties)

    qids = []
    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        qids.append(id)
        nodes.update(ancestors(g,id))
        nodes.update(descendants(g,id))
        nodes.add(id)
    show_subgraph(g, nodes, qids, args)

def cmd_cycles(handle, args):
    g = retrieve_filtered_graph(handle, args)

    cycles = nx.simple_cycles(g)
    print(list(cycles))
    
def cmd_search(handle, args):
    for t in args.terms:
        results = search(handle, t)
        for r in results:
            print(r)

def show_subgraph(g, nodes, query_ids, args):
    """
    Writes graph
    """
    w = GraphRenderer.create(args.to)
    if args.outfile is not None:
        w.outfile = args.outfile
    w.write_subgraph(g, nodes, query_ids=query_ids, container_predicates=args.container_properties)
            
def resolve_ids(g, ids, args):
    r_ids = []
    for id in ids:
        if len(id.split(":")) ==2:
            r_ids.append(id)
        else:
            matches = [n for n in g.nodes() if g.node[n].get('label') == id]
            r_ids += matches
    return r_ids

    
if __name__ == "__main__":
    main()
