#!/usr/bin/env python

"""
Command line wrapper to biogolr library.

Type:

    qbiogorl -h

For instructions

"""

import argparse
from biogolr.golr_associations import search_associations_compact
from obographs.sparql2ontology import *
from obographs.graph_io import *
from obographs.graph_manager import retrieve_filtered_graph
import networkx as nx
from networkx.algorithms.dag import ancestors, descendants
from networkx.drawing.nx_pydot import write_dot
from prefixcommons.curie_util import expand_uri
#from biogolr.golr_associations import search_associations, search_associations_compact, GolrFields, select_distinct_subjects, get_objects_for_subject, get_subjects_for_object

def main():
    """
    Wrapper for OGR
    """

    parser = argparse.ArgumentParser(description='Wrapper for obographs library'
                                                 """
                                                 By default, ontologies are cached locally and synced from a remote sparql endpoint
                                                 """,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--resource', type=str, required=False,
                        help='Name of ontology')
    parser.add_argument('-d', '--dotfile', type=str, required=False,
                        help='Path to dot file to output')
    parser.add_argument('-t', '--to', type=str, required=False,
                        help='Output to (tree, dot, ...)')
    parser.add_argument('-c', '--category', type=str, required=False,
                        help='Category')
    parser.add_argument('-s', '--species', type=str, required=False,
                        help='NCBITaxon ID')
    parser.add_argument('-p', '--properties', nargs='*', type=str, required=False,
                        help='Properties')
    parser.add_argument('-n', '--no-cache', type=bool, required=False,
                        help='Properties')

    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    
    # SUBCOMMAND
    parser_n = subparsers.add_parser('query', aliases='q', help='search by label')
    parser_n.set_defaults(function=cmd_query)
    parser_n.add_argument('ids',nargs='*')
        
    args = parser.parse_args()
    ont = args.resource
    
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
    
def cmd_query(ont, args):
    g = retrieve_filtered_graph(ont, predicates=args.properties)

    w = GraphRenderer.create(args.to)
    
    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        nodes.add(id)
        assocs = search_associations_compact(object=id,
                                             subject_taxon=args.species,
                                             rows=1000,
                                             subject_category=args.category)
        assocs += search_associations_compact(subject=id,
                                              object_taxon=args.species,
                                              rows=1000,
                                              object_category=args.category)
        for a in assocs:
            print(a)
            for x in a['objects']:
                print('  '+w.render_noderef(g,x))

def cmd_map2slim(ont, args):
    g = get_digraph_wrap(ont, args)

    subset_term_ids = get_terms_in_subset(ont, args.slim)
    nodes = set()
    for id in resolve_ids(g, args.ids, args):
        nodes.add(id)
        assocs = search_associations(object=id,
                                     subject_taxon=args.species,
                                     slim=subset_term_ids,
                                     rows=0,
                                     subject_category=args.category)
        for a in assocs:
            print(a)
            for x in a['objects']:
                print('  '+pp_node(g,x,args))
                

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
