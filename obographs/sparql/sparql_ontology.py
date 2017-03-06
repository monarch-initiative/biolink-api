"""
Represents an ontology
"""

import networkx as nx
import logging
import obographs.ontol
from obographs.ontol import Ontology
from obographs.sparql.sparql_ontol_utils import get_digraph, get_named_graph, run_sparql


class RemoteSparqlOntology(Ontology):
    """
    Local or remote ontology
    """

    def extract_subset(self, subset):
        """
        Find all nodes in a subset.
    
        We assume the oboInOwl encoding of subsets, and subset IDs are IRIs
        """
        namedGraph = get_named_graph(ont)
    
        # note subsets have an unusual encoding
        query = """
        prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl>
        SELECT ?c ? WHERE {{
        GRAPH <{g}>  {{
        ?c oboInOwl:inSubset ?s ;
           rdfs:label ?l
        FILTER regex(?s,'#{s}$','i')
        }}
        }}
        """.format(s=subset, g=namedGraph)
        bindings = run_sparql(query)
        return [(r['c']['value'],r['l']['value']) for r in bindings]

    def resolve_names(self, names, is_remote=False, **args):
        if not is_remote:
            return super().resolve_names(names, **args)
        else:
            results = []
            for name in names:
                results += self._search(name)
            logging.info("REMOT RESULTS="+str(results))
            return results
        
    def _search(self, searchterm):
        """
        Search for things using labels
        """
        # TODO: DRY with sparql_ontol_utils
        searchterm = searchterm.replace('%','.*')
        namedGraph = get_named_graph(self.handle)
        query = """
        SELECT ?c WHERE {{
        GRAPH <{g}>  {{
        ?c rdfs:label ?l
        FILTER regex(?l,'{s}','i')
        }}
        }}
        """.format(s=searchterm, g=namedGraph)
        bindings = run_sparql(query)
        return [r['c']['value'] for r in bindings]
            
    
class EagerRemoteSparqlOntology(RemoteSparqlOntology):
    """
    Local or remote ontology
    """

    def __init__(self, handle=None):
        """
        initializes based on an ontology name
        """
        self.handle = handle
        logging.info("Creating eager-remote-sparql from "+str(handle))
        g = get_digraph(handle, None, True)
        logging.info("Graph:"+str(g))
        self.graph = g
        logging.info("Graph "+str(self.graph))

    def __str__(self):
        return "h:{} g:{}".format(self.handle, self.graph)




class LazyRemoteSparqlOntology(RemoteSparqlOntology):
    """
    Local or remote ontology
    """

    def __init__(self):
        pass

    
