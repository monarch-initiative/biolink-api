__author__ = 'cjm'

import logging
import requests

from biolink.util.model.BBOPGraph import *
from biolink.util.model.Concept import *
from biolink.util.model.EntityAnnotationResults import *

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

    def neighbors(self, id=None, params={}):
        response = self.get_response("graph/neighbors", id, "json", params)
        if (response.status_code != 200):
            print("UH-OH:"+str(response))
        return BBOPGraph(response.json())

    def graph(self, id=None, params={}):
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

    def get_response(self, path="", q=None, format=None, payload={}):
        url = self.url_prefix + path;
        if q is not None:
            url += "/" +q;
        if format is not None:
            url = url  + "." + format;
        r = requests.get(url, params=payload)
        return r
