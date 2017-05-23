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
HAS_ROLE = 'http://purl.obolibrary.org/obo/RO_0000087'
ENCODES = 'RO:0002205'
HAS_DBXREF = 'OIO:hasDbXref'

class SciGraph:
    """
    Facade object for accessing a SciGraph instance.

    This provides access to both generic methods following a graph-oriented model, and
    domain-specific convenience methods that build in knowledge of different relationship types.

    """

    def __init__(self, url=None):
        if url is not None:
            self.url_prefix = url
        else:
            self.url_prefix = "http://scigraph-ontology.monarchinitiative.org/scigraph/"
        return

    def neighbors(self, id=None, **params):
        """
        Get neighbors of a node

        parameters are directly passed through to SciGraph: e.g. depth, relationshipType

        Returns a BBOPGraph
        """
        response = self.get_response("graph/neighbors", id, "json", **params)
        return BBOPGraph(response.json())

    def node(self, id=None, **params):
        """
        Get a node in a graph plus its metadata

        Returns a BBOPGraph Node
        """
        response = self.get_response("graph", q=id, format="json", **params)
        nodes = response.json()['nodes']
        return self.make_NamedObject(**nodes[0])

    def bioobject(self, id=None, class_name='BioObject', **params):
        """
        Get a node in a graph and translates it to biomodels datamodel

        Arguments
        ---------
        id
            identifier or CURIE

        class_name
            name of the class in the biomodel data model to instantiate

        Returns: biomodel.BioObject or subclass
        """
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
        """
        Extracts a subgraph around a given in

        Graph includes superclass closure, equivalent classes and direct subclasses

        Returns a BBOPGraph
        """
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

        See https://www.w3.org/Submission/CBD/
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

    def extract_subgraph(self, ids=[], relationshipType='subClassOf'):
        """
        Returns subgraph module extracted using list of node IDs as seed
        """
        g=BBOPGraph()
        visited=[]
        while len(ids)>0:
            id = ids.pop()
            nextg = self.neighbors(id, {'blankNodes':False, relationshipType: relationshipType, 'direction':'OUTGOING','depth':1})
            for edge in nextg.edges:
                next_id = edge.obj
                if next_id not in visited:
                    ids.append(next_id)
                    visited.append(next_id)
            g.merge(nextg)
        return g
    
    # TODO - direct SciGraph method?
    def traverse_chain(self, id=None, rels=[], type=None, blank=True):
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
                                       blankNodes=blank,
                                       relationshipType=nextrel,
                                       direction='OUTGOING',
                                       depth=1)
                for n in nextg.nodes:
                    nmap[n.id] = n
                for e in nextg.edges:
                    if not blank and e.obj.startswith(":"):
                        continue
                    stack.append( (e.obj, nextrels.copy()) )
                
        sinknodes = [nmap[x] for x in sinks]
        if type is not None:
            sinknodes = [x for x in sinknodes if type in x.meta.pmap['types']]
        return sinknodes
            
    
    def autocomplete(self, term=None):
        """
        Directly wraps SciGraph autocomplete
        """
        response = self.get_response("vocabulary/autocomplete", term)
        return response.json()['list']

    def search(self, term=None):
        """
        Directly wraps SciGraph search
        """
        response = self.get_response("vocabulary/search", term)
        concepts = []
        for r in response.json()['concepts']:
            concepts.append(Concept(r))
        return concepts

    def annotate(self, content=None):
        """
        Directly wraps SciGraph annotate
        """
        ## TODO: post not get
        response = self.get_response("annotations/entities", None, "json", {'content':content, 'longestOnly':True})
        return EntityAnnotationResults(response.json(), content)

    # Internal wrapper onto requests API
    def get_response(self, path="", q=None, format=None, **params):
        url = self.url_prefix + path;
        if q is not None:
            url += "/" +q;
        if format is not None:
            url = url  + "." + format;
        r = requests.get(url, params=params)
        return r

    # Simple mapping from bbop graphs to domain-specific objects
    def make_NamedObject(self, class_name='NamedObject', **kwargs):
        module = importlib.import_module("biomodel.core")
        DynClass = getattr(module, class_name)
        return DynClass(**self.map_tuple(**kwargs))

    # Maps bbop-graph model to biomodels datamodel
    # TODO: consider using biomodels directly
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

    ## Domain-specific methods
    ## Note some of these may be redundant with https://github.com/monarch-initiative/monarch-cypher-queries/tree/master/src/main/cypher/golr-loader

    def gene_to_uniprot_proteins(self, id):
        """
        Given a gene ID, find the list of uniprot proteins that this encodes

        This method may be retired in future. See https://github.com/monarch-initiative/dipper/issues/461
        """
        objs = self.traverse_chain(id, [ENCODES, HAS_DBXREF], blank=False)
        return [x.id for x in objs]

    def phenotype_to_entity_list(self, id):
        """
        Given a phenotype ID, find the list of affected entities

        Uses the Ontology Design Pattern has-part o inheres_in
        """
        objs = self.traverse_chain(id, [HAS_PART, INHERES_IN], "anatomical entity")
        return [self.make_NamedObject(id=x.id, lbl=x.lbl, meta={}, class_name='NamedObject') for x in objs]

    def substance_to_role_associations(self, id):
        """
        Given a chemical ID, find the list of roles

        Uses the Ontology Design Pattern CHEMICAL has-role ROLE
        """
        # TODO - include closure
        bbg = self.neighbors(id, relationshipType=HAS_ROLE, depth=1)
        return bbg_to_assocs(bbg)

    def substance_participates_in_associations(self, id):
        """
        Given a chemical ID, find the list of activities and processes that have this as participant

        Uses GO-CHEBI axioms
        """
        # TODO - include closure
        bbg = self.neighbors(id, direction='INCOMING', depth=1)
        return bbg_to_assocs(bbg)
    

def bbg_to_assocs(g):
    return [bbedge_to_assoc(e,g) for e in g.edges]

def bbedge_to_assoc(e,g):
    return {
        'subject': {'id': e.sub,
                    'label': g.get_lbl(e.sub)
                    },
        'object': {'id': e.obj,
                   'label': g.get_lbl(e.obj)
                    },
        }
        
    
