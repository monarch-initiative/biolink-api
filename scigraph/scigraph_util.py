__author__ = 'cjm'

import logging
import requests
import importlib

from scigraph.model.BBOPGraph import *
from scigraph.model.Concept import *
from scigraph.model.EntityAnnotationResults import *
from biomodel.core import NamedObject, BioObject, SynonymPropertyValue

# TODO: modularize into vocab/graph/etc?

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
    def make_BioObject(self, **kwargs):
        return NamedObject(**self.map_tuple(**kwargs))

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
    
