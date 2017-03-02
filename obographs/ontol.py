"""
Represents an ontology
"""

import networkx as nx
import logging
import obographs.obograph_util as obograph_util
import re

class Ontology():
    """
    Local or remote ontology
    """

    def __init__(self, handle=None, graph=None, graphdoc=None):
        """
        initializes based on an ontology name
        """
        self.handle = handle

        # networkx object
        self.graph = graph

        # obograph
        self.graphdoc = graphdoc

    def get_graph(self):
        """
        Returns a networkx graph for the whole ontology.

        Only implemented for eager methods
        """
        return self.graph

    # consider caching
    def get_filtered_graph(self, relations=None):
        """
        Returns a networkx graph for the whole ontology, for a subset of relations

        Only implemented for eager methods
        """
        # default method - wrap get_graph
        srcg = self.get_graph()
        if relations is None:
            logging.info("No filtering on "+str(self))
            return srcg
        logging.info("Filtering {} for {}".format(self, relations))
        g = nx.MultiDiGraph()
    
        logging.info("copying nodes")
        for n,d in srcg.nodes_iter(data=True):
            g.add_node(n, attr_dict=d)

        logging.info("copying edges")
        num_edges = 0
        for x,y,d in srcg.edges_iter(data=True):
            if d['pred'] in relations:
                num_edges += 1
                g.add_edge(x,y,attr_dict=d)
        logging.info("Filtered edges: {}".format(num_edges))
        return g
    
    def subgraph(self, nodes=[]):
        """
        Returns an induced subgraphs

        By default this wraps networkx subgraph,
        but may be overridden 
        """
        return self.get_graph().subgraph(nodes)
                
    def extract_subset(self, subset):
        """
        Find all nodes in a subset.
    
        We assume the oboInOwl encoding of subsets, and subset IDs are IRIs
        """
        pass

    def nodes(self):
        """
        Wraps networkx by default
        """
        return self.get_graph().nodes()

    def ancestors(self, node, relations=None):
        """
        Wraps networkx by default
        """
        g = None
        if relations is None:
            g = self.get_graph()
        else:
            g = self.get_filtered_graph(relations)
        return nx.ancestors(g, node)

    def descendants(self, node, relations=None):
        """
        Wraps networkx by default
        """
        g = None
        if relations is None:
            g = self.get_graph()
        else:
            g = self.get_filtered_graph(relations)
        return nx.descendants(g, node)

    def logical_definitions(self, node, relations=None):
        """
        Retrieves logical definitions for a class
        """
        pass
    
    def resolve_names(self, names, **args):
        g = self.get_graph()
        r_ids = []
        for n in names:
            if len(n.split(":")) ==2:
                r_ids.append(n)
            else:
                matches = [nid for nid in g.nodes() if self.is_match(g.node[nid], n, **args)]
                r_ids += matches
        return r_ids

    def is_match(self, node, term, is_partial_match=False, is_regex=False, **args):
        label = node.get('label')
        if term == '%':
            return True
        if label is None:
            label = ''
        if term.find('%') > -1:
            term = term.replace('%','.*')
            is_regex = True
        if is_regex:
            return re.search(term, label) is not None
        if is_partial_match:
            return label.find(term) > -1
        else:
            return label == term
    
    def search(self, searchterm, **args):
        """
        Simple search
        """
        return self.resolve_names([searchterm], **args)
