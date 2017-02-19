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
import logging

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
    parser.add_argument('-p', '--properties', nargs='*', type=str, required=False,
                        help='Properties')
    parser.add_argument('-n', '--no-cache', type=bool, required=False,
                        help='Do not cache')

    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    
    # SUBCOMMAND
    parser_n = subparsers.add_parser('search', aliases='s', help='search by label')
    parser_n.set_defaults(function=cmd_search)
    parser_n.add_argument('terms',nargs='*')
    
    parser_n = subparsers.add_parser('ancestors', aliases='a', help='Checks URLs')
    parser_n.set_defaults(function=cmd_ancestors)
    parser_n.add_argument('ids',nargs='*')

    parser_n = subparsers.add_parser('descendants', aliases='d', help='Checks URLs')
    parser_n.set_defaults(function=cmd_descendants)
    parser_n.add_argument('ids',nargs='*')

    parser_n = subparsers.add_parser('graph', aliases='g', help='Checks URLs')
    parser_n.set_defaults(function=cmd_graph)
    parser_n.add_argument('ids',nargs='*')

    parser_n = subparsers.add_parser('cycles', help='Checks URLs')
    parser_n.set_defaults(function=cmd_cycles)
    
    args = parser.parse_args()
    ont = args.resource
    
    func = args.function
    func(ont, args)

def get_digraph_wrap(ont, args):
    props = []
    if args.properties is not None:
        for p in args.properties:
            props.append(p)
    g = get_digraph(ont, props, True)
    return g
    
def cmd_ancestors(ont, args):
    g = get_digraph_wrap(ont, args)

    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        nodes.update(ancestors(g,id))
        nodes.add(id)
    show_subgraph(g, nodes, args)

def cmd_descendants(ont, args):
    g = get_digraph_wrap(ont, args)

    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        nodes.update(descendants(g,id))
        nodes.add(id)
    show_subgraph(g, nodes, args)

def cmd_graph(ont, args):
    g = get_digraph_wrap(ont, args)

    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        nodes.update(ancestors(g,id))
        nodes.update(descendants(g,id))
        nodes.add(id)
    show_subgraph(g, nodes, args)

def cmd_cycles(ont, args):
    g = get_digraph_wrap(ont, args)

    cycles = nx.simple_cycles(g)
    print(list(cycles))
    
def cmd_search(ont, args):
    for t in args.terms:
        results = search(ont, t)
        for r in results:
            print(r)

def show_subgraph(g, nodes, args):
    """
    Writes graph
    """
    w = GraphRenderer.create(args.to)
    if args.outfile is not None:
        w.outfile = args.outfile
    w.write_subgraph(g, nodes)
            
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
