"""
Represents an ontology
"""

import networkx as nx
import logging
import obographs.obograph_util as obograph_util

class Ontology():
    """
    Local or remote ontology
    """

    def __init__(self, handle=None, graph=None):
        """
        initializes based on an ontology name
        """
        self.handle = handle
        self.graph = graph

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
        g = networkx.MultiDiGraph()
    
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
    
