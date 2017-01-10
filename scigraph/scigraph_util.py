__author__ = 'cjm'

"""
Utility classes for wrapping a SciGraph service
"""

import logging
import requests
import importlib

from scigraph.model.BBOPGraph import *
from scigraph.model.Concept import *
from scigraph.model.EntityAnnotationResults import *
from biomodel.core import NamedObject, BioObject, SynonymPropertyValue

# TODO: modularize into vocab/graph/etc?

HAS_PART = 'http://purl.obolibrary.org/obo/BFO_0000051'
INHERES_IN = 'http://purl.obolibrary.org/obo/RO_0000052'

class SciGraph:
    """
    foo
    """

    def __init__(self, url=None):
        if url is not None:
            self.url_prefix = url
        else:
            self.url_prefix = "http://scigraph-ontology.monarchinitiative.org/scigraph/"
        return

    def neighbors(self, id=None, **params):
        response = self.get_response("graph/neighbors", id, "json", **params)
        return BBOPGraph(response.json())

    def node(self, id=None, **params):
        response = self.get_response("graph", q=id, format="json", **params)
        nodes = response.json()['nodes']
        return self.make_NamedObject(**nodes[0])

    def bioobject(self, id=None, class_name='BioObject', **params):
        response = self.get_response("graph/neighbors",
                                     q=id, format="json", depth=1,
                                     relationshipType='http://purl.obolibrary.org/obo/RO_0002162', **params)
        nodes = response.json()['nodes']
        t=None
        obj=None
        for n in nodes:
            if n['id'] == id:
                obj = self.make_NamedObject(**n, class_name=class_name)
            else:
                t = self.make_NamedObject(**n)
        obj.taxon = t
        return obj
        
    def graph(self, id=None, depth=0):
        g1 = self.neighbors(id, {'relationshipType':'subClassOf', 'blankNodes':'false', 'direction':'OUTGOING','depth':20})
        g2 = self.neighbors(id, {'relationshipType':'subClassOf', 'direction':'INCOMING','depth':1})
        g3 = self.neighbors(id, {'relationshipType':'equivalentClass', 'depth':1})
        g1.merge(g2)
        g1.merge(g3)
        return g1

    # TODO: replace with https://github.com/SciGraph/SciGraph/issues/200
    def cbd(self, id=None):
        """
        Returns the Concise Bounded Description of a node
        """
        nodes = [id]
        g=BBOPGraph()
        while len(nodes)>0:
            n = nodes.pop()
            nextg = self.neighbors(n, {'blankNodes':True, 'direction':'OUTGOING','depth':1})
            for nn in nextg.nodes:
                if nn.id.startswith("_:"):
                    n.append(nn.id)
            g.merge(nextg)
        return g

    # TODO - direct SciGraph method?
    def traverse_chain(self, id=None, rels=[], type=None):
        """
        Finds all nodes reachable via a specified chain of relationship types
        """

        relsr = rels.copy()
        relsr.reverse()
        
        # list of tuples
        stack = [ (id, relsr) ]

        nmap = {}
        sinks = []
        while len(stack)>0:
            (nextid, nextrels) = stack.pop()
            if len(nextrels) == 0:
                sinks.append(nextid)
            else:
                nextrel = nextrels.pop()
                nextg = self.neighbors(nextid,
                                       blankNodes=True,
                                       relationshipType=nextrel,
                                       direction='OUTGOING',
                                       depth=1)
                for n in nextg.nodes:
                    nmap[n.id] = n
                for e in nextg.edges:
                    stack.append( (e.obj, nextrels.copy()) )
                
        sinknodes = [nmap[x] for x in sinks]
        if type is not None:
            sinknodes = [x for x in sinknodes if type in x.meta.pmap['types']]
        return sinknodes
            
    
    def autocomplete(self, term=None):
        response = self.get_response("vocabulary/autocomplete", term)
        return response.json()['list']

    def search(self, term=None):
        response = self.get_response("vocabulary/search", term)
        concepts = []
        for r in response.json()['concepts']:
            concepts.append(Concept(r))
        return concepts

    def annotate(self, content=None):
        ## TODO: post not get
        response = self.get_response("annotations/entities", None, "json", {'content':content, 'longestOnly':True})
        return EntityAnnotationResults(response.json(), content)

    def get_response(self, path="", q=None, format=None, **params):
        url = self.url_prefix + path;
        if q is not None:
            url += "/" +q;
        if format is not None:
            url = url  + "." + format;
        r = requests.get(url, params=params)
        return r

    def make_NamedObject(self, class_name='NamedObject', **kwargs):
        module = importlib.import_module("biomodel.core")
        DynClass = getattr(module, class_name)
        return DynClass(**self.map_tuple(**kwargs))

    def map_tuple(self, id, lbl, meta):
        obj = {
            'id':id,
            'label':lbl,
            'categories':meta.get('category'),
            'xrefs':meta.get('http://www.geneontology.org/formats/oboInOwl#hasDbXref'),
            
        }
        if 'synonym' in meta:
            obj['synonyms'] = [SynonymPropertyValue(pred='synonym', val=s) for s in meta['synonym']]
        return obj

    def phenotype_to_entity_list(self, id):
        objs = self.traverse_chain(id, [HAS_PART, INHERES_IN], "anatomical entity")
        return [self.make_NamedObject(id=x.id, lbl=x.lbl, meta={}, class_name='NamedObject') for x in objs]
