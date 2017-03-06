"""
A module for representing simple graph-oriented views of an ontology

See also:

 - ontol_factory.py

"""

import networkx as nx
import logging
import obographs.obograph_util as obograph_util
import re

class Ontology():
    """An object that represents a basic graph-oriented view over an ontology.

    The ontology may be represented in memory, or it may be located
    remotely. See subclasses for details.

    The default implementation is an in-memory wrapper onto the python networkx library

    """

    def __init__(self, handle=None, graph=None, graphdoc=None):
        """
        initializes based on an ontology name.

        Note: do not call this directly, use OntologyFactory instead
        """
        self.handle = handle

        # networkx object
        self.graph = graph

        # obograph
        self.graphdoc = graphdoc

    def get_graph(self):
        """
        Returns a networkx graph for the whole ontology.

        Only implemented for 'eager' implementations 
        """
        return self.graph

    # consider caching
    def get_filtered_graph(self, relations=None):
        """
        Returns a networkx graph for the whole ontology, for a subset of relations

        Only implemented for eager methods.

        Implementation notes: currently this is not cached
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
        Returns an induced subgraph

        By default this wraps networkx subgraph,
        but this may be overridden in specific implementations
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
        Returns all nodes in ontology

        Wraps networkx by default
        """
        return self.get_graph().nodes()

    def ancestors(self, node, relations=None):
        """
        Returns all ancestors of specified node.

        Wraps networkx by default.

        Arguments
        ---------

        node: string

           identifier for node in ontology

        relations: list of strings

           list of relation (object property) IDs used to filter

        """
        g = None
        if relations is None:
            g = self.get_graph()
        else:
            g = self.get_filtered_graph(relations)
        if node in g:
            return nx.ancestors(g, node)
        else:
            return []

    def descendants(self, node, relations=None):
        """
        Returns all ancestors of specified node.

        Wraps networkx by default.

        Arguments as for ancestors
        """
        g = None
        if relations is None:
            g = self.get_graph()
        else:
            g = self.get_filtered_graph(relations)
        if node in g:
            return nx.descendants(g, node)
        else:
            return []

    def parent_index(self, relations=None):
        """
        Returns a list of lists, where the inner list is [CHILD, PARENT1, ..., PARENT2]
        """
        g = None
        if relations is None:
            g = self.get_graph()
        else:
            g = self.get_filtered_graph(relations)
        l = []
        for n in g:
            l.append([n] ++ g.predecessors(b))
        return l
        
    def logical_definitions(self, node, relations=None):
        """
        Retrieves logical definitions for a class
        """
        pass
    
    def resolve_names(self, names, **args):
        """
        returns a list of identifiers based on an input list of labels and identifiers.

        Arguments
        ---------

        is_regex : boolean

           if true, treats each name as a regular expression

        is_partial_match : boolean

           if true, treats each name as a regular expression .*name.*

        """
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
        Simple search. Returns list of IDs.

        Arguments: as for resolve_names
        """
        return self.resolve_names([searchterm], **args)

