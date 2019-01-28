__author__ = 'cjm'

import logging
import requests

# TODO: consider an external model

class BBOPGraph:

    """
    foo
    """

    nodemap = {}

    def __init__(self, obj={}):
        self.nodes = []
        self.edges = []
        self.add_json_graph(obj)
        return

    def add_json_graph(self, obj={}):
        #print(obj)
        for n in obj['nodes']:
            self.add_node(Node(**n))
        for e in obj['edges']:
            self.add_edge(Edge(e))
        #print("EDGES="+str(self.edges))

    def add_node(self, n) :
        self.nodemap[n.id] = n
        self.nodes.append(n)

    def add_edge(self, e) :
        self.edges.append(e)

    def merge(self,g):
        for n in g.nodes:
            self.add_node(n)
        for e in g.edges:
            self.add_edge(e)

    def get_node(self, id) :
        return self.nodemap[id]

    def get_lbl(self, id) :
        return self.nodemap[id].lbl

    def get_root_nodes(self, relations=[]):
        roots = []
        for n in self.nodes:
            if (len(self.get_outgoing_edges(n.id, relations)) == 0):
                roots.append(n)
        return roots

    def get_leaf_nodes(self, relations=[]):
        roots = []
        for n in self.nodes:
            if (len(self.get_incoming_edges(n.id, relations)) == 0):
                roots.append(n)
        return roots

    def get_outgoing_edges(self, nid, relations=[]):
        el = []
        for e in self.edges:
            if (e.sub == nid):
                if (len(relations) == 0 or e.pred in relations):
                    el.append(e)
        return el

    def get_incoming_edges(self, nid, relations=[]):
        el = []
        for e in self.edges:
            if (e.obj == nid):
                if (len(relations) == 0 or e.pred in relations):
                    el.append(e)
        return el

class Node:
    def __init__(self, id, lbl=None, meta=None):    
        self.id = id
        self.lbl = lbl
        self.meta = Meta(meta)
    def __str__(self):
        return self.id+' "'+str(self.lbl)+'"'

    def as_dict(self):
        return {
            "id": self.id,
            "lbl": self.lbl,
            "meta": self.meta.pmap
        }


class Edge:
    def __init__(self, obj={}):    
        self.sub = obj['sub']
        self.pred = obj['pred']
        self.obj = obj['obj']
    
    def __str__(self):
        return self.sub +"-["+self.pred+"]->"+self.obj


class Meta:
    def __init__(self, obj={}):    
        self.type_list = obj['types']
        self.category_list = []
        if 'category' in obj:
            self.category_list = obj['category']
        self.pmap = obj
