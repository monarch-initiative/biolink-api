#!/usr/bin/env python

"""
Command line wrapper to obographs assocmodel library

Type:

    ogr-assoc -h

For instructions

Examples:

```
ogr-assoc -r go -T NBCITaxon:9606 -C gene function enrichment -q GO:1903010 

ogr-assoc -v -r go -T NCBITaxon:10090 -C gene function dendrogram GO:0003700 GO:0005215 GO:0005634 GO:0005737 GO:0005739 GO:0005694 GO:0005730  GO:0000228 GO:0000262 

ogr-assoc -v -r go -T NCBITaxon:10090 -C gene function simmatrix MGI:1890081 MGI:97487 MGI:106593 MGI:97250 MGI:2151057 MGI:1347473

```

"""

import argparse
import networkx as nx
from networkx.algorithms.dag import ancestors, descendants
from ontobio.assoc_factory import AssociationSetFactory
from ontobio.ontol_factory import OntologyFactory
from ontobio.graph_io import GraphRenderer
from ontobio.slimmer import get_minimal_subgraph
import logging

def main():
    """
    Wrapper for OGR Assocs
    """
    parser = argparse.ArgumentParser(description='Wrapper for obographs assocmodel library'
                                                 """
                                                 By default, ontologies and assocs are cached locally and synced from a remote sparql endpoint
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
    parser.add_argument('-s', '--search', type=str, default='', required=False,
                        help='Search type. p=partial, r=regex')
    parser.add_argument('-S', '--slim', type=str, default='', required=False,
                        help='Slim type. m=minimal')
    parser.add_argument('-c', '--container_properties', nargs='*', type=str, required=False,
                        help='Properties to nest in graph')
    parser.add_argument('-C', '--category', nargs=2, type=str, required=True,
                        help='category tuple (SUBJECT OBJECT)')
    parser.add_argument('-T', '--taxon', type=str, required=True,
                        help='Taxon of associations')
    parser.add_argument('-v', '--verbosity', default=0, action='count',
                        help='Increase output verbosity')

    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    
    # ENRICHMENT
    parser_n = subparsers.add_parser('enrichment', help='Perform an enrichment test')
    parser_n.add_argument('-q', '--query',type=str, help='query all genes for this class an use as subject')
    parser_n.add_argument('-H', '--hypotheses',nargs='*', help='list of classes to test against')
    parser_n.add_argument('subjects',nargs='*')
    parser_n.set_defaults(function=run_enrichment_test)
    
    # QUERY
    parser_n = subparsers.add_parser('query', help='Query based on positive and negative terms')
    parser_n.add_argument('-q', '--query',nargs='*', help='positive classes')
    parser_n.add_argument('-N', '--negative',type=str, help='negative classes')
    parser_n.set_defaults(function=run_query)

    # INTERSECTIONS
    parser_n = subparsers.add_parser('intersections', help='Query intersections')
    parser_n.add_argument('-X', '--xterms',nargs='*', help='x classes')
    parser_n.add_argument('-Y', '--yterms',nargs='*', help='y classes')
    parser_n.add_argument('--useids',type=bool, default=False, help='if true, use IDs not labels on axes')
    parser_n.add_argument('terms',nargs='*', help='all terms (x and y)')
    parser_n.set_defaults(function=plot_intersections)

    # INTERSECTION DENDROGRAM
    parser_n = subparsers.add_parser('dendrogram', help='Plot dendrogram from intersections')
    parser_n.add_argument('-X', '--xterms',nargs='*', help='x classes')
    parser_n.add_argument('-Y', '--yterms',nargs='*', help='y classes')
    parser_n.add_argument('--useids',type=bool, default=False, help='if true, use IDs not labels on axes')
    parser_n.add_argument('terms',nargs='*', help='all terms (x and y)')
    parser_n.set_defaults(function=plot_term_intersection_dendrogram)

    # SIMILARITY MATRIX
    parser_n = subparsers.add_parser('simmatrix', help='Plot dendrogram for similarities between subjects')
    parser_n.add_argument('-X', '--xsubjects',nargs='*', help='x subjects')
    parser_n.add_argument('-Y', '--ysubjects',nargs='*', help='y subjects')
    parser_n.add_argument('--useids',type=bool, default=False, help='if true, use IDs not labels on axes')
    parser_n.add_argument('subjects',nargs='*', help='all terms (x and y)')
    parser_n.set_defaults(function=plot_simmatrix)

    args = parser.parse_args()

    if args.verbosity >= 2:
        logging.basicConfig(level=logging.DEBUG)
    if args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    logging.info("Welcome!")
    
    handle = args.resource

    # Ontology Factory
    ofactory = OntologyFactory()
    logging.info("Creating ont object from: {} {}".format(handle, ofactory))
    ont = ofactory.create(handle)
    logging.info("ont: {}".format(ont))

    # Association Factory
    afactory = AssociationSetFactory()
    [subject_category, object_category] = args.category
    aset = afactory.create(ontology=ont,
                           subject_category=subject_category,
                           object_category=object_category,
                           taxon=args.taxon)
    
    
    func = args.function
    func(ont, aset, args)

def run_enrichment_test(ont, aset, args):
    subjects = args.subjects
    if args.query is not None:
        subjects = aset.query([args.query])
    print("SUBJECTS q={} : {}".format(args.query, subjects))
    enr = aset.enrichment_test(subjects=subjects, hypotheses=args.hypotheses, labels=True)
    for r in enr:
        print("{:8.3g} {} {:40s}".format(r['p'],r['c'],str(r['n'])))

def run_query(ont, aset, args):
    subjects = aset.query(args.query, args.negative)
    for s in subjects:
        print("{} {}".format(s, str(aset.label(s))))

def create_intersection_matrix(ont, aset, args):
    xterms = args.xterms
    yterms = args.yterms
    if args.terms is not None and len(args.terms) > 0:
        xterms = args.terms
    if yterms is None or len(yterms) == 0:
        yterms = xterms
    logging.info("X={} Y={}".format(xterms,yterms))
    ilist = aset.query_intersections(x_terms=xterms, y_terms=yterms)
    z, xaxis, yaxis = aset.intersectionlist_to_matrix(ilist, xterms, yterms)
    xaxis = mk_axis(xaxis, ont, args)
    yaxis = mk_axis(yaxis, ont, args)
    return (z, xaxis, yaxis)

def plot_intersections(ont, aset, args):
    import plotly.plotly as py
    import plotly.graph_objs as go
    (z, xaxis, yaxis) = create_intersection_matrix(ont, aset, args)
    trace = go.Heatmap(z=z,
                       x=xaxis,
                       y=yaxis)
    data=[trace]
    py.plot(data, filename='labelled-heatmap')

def plot_simmatrix(ont, aset, args):
    import numpy as np
    xsubjects = args.xsubjects
    ysubjects = args.ysubjects
    if args.subjects is not None and len(args.subjects) > 0:
        xsubjects = args.subjects
    if ysubjects is None or len(ysubjects) == 0:
        ysubjects = xsubjects
    (z, xaxis, yaxis) = aset.similarity_matrix(xsubjects, ysubjects)
    xaxis = mk_axis(xaxis, aset, args)
    yaxis = mk_axis(yaxis, aset, args)
    z = np.array(z)
    z = -z
    print("Z={}".format(z))
    plot_dendrogram(z, xaxis, yaxis)
    
def plot_term_intersection_dendrogram(ont, aset, args):
    import numpy as np
    # TODO: currently only works for xaxis=yaxis
    (z, xaxis, yaxis) = create_intersection_matrix(ont, aset, args)
    z = np.array(z)
    z = -z
    print("Z={}".format(z))
    plot_dendrogram(z, xaxis, yaxis)
    
def plot_dendrogram(z, xaxis, yaxis):
    import plotly.plotly as py
    import plotly.figure_factory as FF
    import plotly.graph_objs as go
    import numpy as np
    from scipy.cluster.hierarchy import linkage
    from scipy.spatial.distance import pdist, squareform


    # Initialize figure by creating upper dendrogram
    figure = FF.create_dendrogram(z, orientation='bottom', labels=xaxis)
    for i in range(len(figure['data'])):
        figure['data'][i]['yaxis'] = 'y2'

    # Create Side Dendrogram
    # TODO: figure out how to create labels for this axis
    dendro_side = FF.create_dendrogram(z, orientation='right', labels=xaxis)
    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'
        
    # Add Side Dendrogram Data to Figure
    figure['data'].extend(dendro_side['data'])

    # Create Heatmap
    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    #dendro_leaves = list(map(int, dendro_leaves))
    data_dist = pdist(z)
    heat_data = squareform(data_dist)
    #heat_data = heat_data[dendro_leaves,:]
    #heat_data = heat_data[:,dendro_leaves]
    
    heatmap = go.Data([
        go.Heatmap(
            x = dendro_leaves,
            y = dendro_leaves,
            z = heat_data,
            colorscale = 'YIGnBu'
        )
    ])
    heatmap[0]['x'] = figure['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

    # Add Heatmap Data to Figure
    figure['data'].extend(go.Data(heatmap))

    # Edit Layout
    figure['layout'].update({'width':800, 'height':800,
                         'showlegend':False, 'hovermode': 'closest',
                         })
    # Edit xaxis
    figure['layout']['xaxis'].update({'domain': [.15, 1],
                                  'mirror': False,
                                  'showgrid': False,
                                  'showline': False,
                                  'zeroline': False,
                                  'ticks':""})
    # Edit xaxis2
    figure['layout'].update({'xaxis2': {'domain': [0, .15],
                                   'mirror': False,
                                   'showgrid': False,
                                   'showline': False,
                                   'zeroline': False,
                                   'showticklabels': False,
                                   'ticks':""}})

    # Edit yaxis
    figure['layout']['yaxis'].update({'domain': [0, .85],
                                  'mirror': False,
                                  'showgrid': False,
                                  'showline': False,
                                  'zeroline': False,
                                  'showticklabels': False,
                                  'ticks': ""})
    # Edit yaxis2
    figure['layout'].update({'yaxis2':{'domain':[.825, .975],
                                   'mirror': False,
                                   'showgrid': False,
                                   'showline': False,
                                   'zeroline': False,
                                   'showticklabels': False,
                                   'ticks':""}})

    py.plot(figure, filename='dendrogram_with_labels')
    
def mk_axis(terms, kb, args):
    return [label_or_id(x).replace(" ","<br>") for x in terms]

def label_or_id(x, kb):
    label = kb.label(x)
    if label is None:
        return x
    else:
        return label

if __name__ == "__main__":
    main()