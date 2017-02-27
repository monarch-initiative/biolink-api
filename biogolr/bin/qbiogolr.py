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
from obographs.slimmer import get_minimal_subgraph
#from biogolr.golr_associations import search_associations, search_associations_compact, GolrFields, select_distinct_subjects, get_objects_for_subject, get_subjects_for_object
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
    parser.add_argument('-d', '--display', type=str, default='o', required=False,
                        help='What to display: some combination of o, s, r. o=object ancestors, s=subject ancestors. If r present, draws s<->o relations ')
    parser.add_argument('-o', '--outfile', type=str, required=False,
                        help='Path to output file')
    parser.add_argument('-t', '--to', type=str, required=False,
                        help='Output to (tree, dot, ...)')
    parser.add_argument('-C', '--category', type=str, required=False,
                        help='Category')
    parser.add_argument('-c', '--container_properties', nargs='*', type=str, required=False,
                        help='Properties to nest in graph')
    parser.add_argument('-s', '--species', type=str, required=False,
                        help='NCBITaxon ID')
    parser.add_argument('-S', '--slim', type=str, default='', required=False,
                        help='Slim type. m=minimal')
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
    
    nodes = set()

    display = args.display
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

            if display.find('r') > -1:
                pass
            
            if display.find('o') > -1:
                for obj in objs:
                    nodes.add(obj)
                    nodes.update(nx.ancestors(g, obj))

            if display.find('s') > -1:
                sub = a['subject']
                nodes.add(sub)
                nodes.update(nx.ancestors(g, sub))
                
    subg = g.subgraph(nodes)
    if display.find('r') > -1:
        for a in assocs:
            rel = a['relation']
            sub = a['subject']
            objs = a['objects']
            if rel is None:
                rel = 'rdfs:seeAlso'
            for obj in objs:
                logging.info("Adding assoc rel {} {} {}".format(sub,obj,rel))
                subg.add_edge(obj,sub,pred=rel)
            

    show_graph(subg, nodes, objs, args)
            #for x in objs:
            #    print('  '+w.render_noderef(g,x))
            
# TODO
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
                

def show_graph(g, nodes, query_ids, args):
    """
    Writes graph
    """
    if args.slim.find('m') > -1:
        logging.info("SLIMMING")
        g = get_minimal_subgraph(g, query_ids)
    w = GraphRenderer.create(args.to)
    if args.outfile is not None:
        w.outfile = args.outfile
    logging.info("Writing subg from "+str(g))
    w.write(g, query_ids=query_ids, container_predicates=args.container_properties)

    
if __name__ == "__main__":
    main()
