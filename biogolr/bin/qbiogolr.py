#!/usr/bin/env python

"""
Command line wrapper to biogolr library.

Type:

    qbiogorl -h

For instructions

"""

import argparse
from biogolr.golr_associations import search_associations_compact
from obographs.ontol_factory import OntologyFactory
from obographs.graph_io import *
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
    parser.add_argument('-o', '--outfile', type=str, required=False,
                        help='Path to output file')
    parser.add_argument('-t', '--to', type=str, required=False,
                        help='Output to (tree, dot, ...)')
    parser.add_argument('-c', '--category', type=str, required=False,
                        help='Category')
    parser.add_argument('-s', '--species', type=str, required=False,
                        help='NCBITaxon ID')
    parser.add_argument('-p', '--properties', nargs='*', type=str, required=False,
                        help='Properties')

    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    
    # SUBCOMMAND
    parser_n = subparsers.add_parser('query', aliases='q', help='search by label')
    parser_n.set_defaults(function=cmd_query)
    parser_n.add_argument('ids',nargs='*')

    # ontology
    args = parser.parse_args()
    handle = args.resource
    factory = OntologyFactory()
    ont = factory.create(handle)
    
    func = args.function
    func(ont, args)
    
def cmd_query(ont, args):
    """
    Main query command
    """
    g = ont.get_filtered_graph(relations=args.properties)

    w = GraphRenderer.create(args.to)
    
    for id in ont.resolve_names(args.ids):
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
            objs = a['objects']
            nodes = set()
            #nodes.update([ a['subject'] ])
            for obj in objs:
                nodes.add(obj)
                nodes.update(nx.ancestors(g, obj))
            show_subgraph(g, nodes, objs, args)
            #for x in objs:
            #    print('  '+w.render_noderef(g,x))

def cmd_map2slim(ont, args):

    subset_term_ids = ont.extract_subset(args.slim)
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
                

def show_subgraph(g, nodes, query_ids, args):
    """
    Writes graph
    """
    w = GraphRenderer.create(args.to)
    if args.outfile is not None:
        w.outfile = args.outfile
    w.write_subgraph(g, nodes, query_ids=query_ids, container_predicates=None)

    
if __name__ == "__main__":
    main()
