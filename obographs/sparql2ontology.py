"""
Reconsitutes an ontology from SPARQL queries over a remote SPARQL server
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import networkx


# TODO
# for now we assume ontobee
ontol_sources = {
    'go': "http://rdf.geneontology.org/sparql",
    '': "http://sparql.hegroup.org/sparql"
    }


def get_digraph(ont):
    """
    Creates a graph object
    """
    digraph = networkx.MultiDiGraph()
    for (s,p,o) in get_edges(ont):
        digraph.add_edge(s,o,pred=p)
    return digraph

def get_edges(ont):
    """
    Creates a graph object
    """
    edges = [(c,'is_a', 'd') for (c,d) in fetchall_isa(ont)]
    edges += fetchall_svf(ont)
    return edges

def run_sparql(q):
    # TODO: select based on ontology
    #sparql = SPARQLWrapper("http://rdf.geneontology.org/sparql")
    sparql = SPARQLWrapper("http://sparql.hegroup.org/sparql")

    # TODO: iterate over large sets?
    full_q = q + ' LIMIT 50000'
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def get_named_graph(ont):
    """
    Ontobee uses NGs such as http://purl.obolibrary.org/obo/merged/CL
    """

    namedGraph = 'http://purl.obolibrary.org/obo/merged/' + ont.upper()
    return namedGraph

def fetchall_isa(ont):
    namedGraph = get_named_graph(ont)
    queryBody = querybody_isa()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    results = run_sparql(query)
    bindings = results['results']['bindings']
    return [(r['c']['value'],r['d']['value']) for r in bindings]

def fetchall_svf(ont):
    namedGraph = get_named_graph(ont)
    queryBody = querybody_svf()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    results = run_sparql(query)
    bindings = results['results']['bindings']
    return [(r['c']['value'], r['p']['value'], r['d']['value']) for r in bindings]

def fetchall_labels(ont):
    namedGraph = get_named_graph(ont)
    queryBody = querybody_label()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    results = run_sparql(query)
    bindings = results['results']['bindings']
    return [(r['c']['value'], r['p']['value'], r['d']['value']) for r in bindings]

def querybody_isa():
    return """
    { ?c rdfs:subClassOf ?d }
    FILTER (!isBlank(?c))
    FILTER (!isBlank(?d))
    """

def querybody_svf():
    return """
    { ?c rdfs:subClassOf [owl:onProperty ?p ; owl:someValuesFrom ?d ] }
    FILTER (!isBlank(?c))
    FILTER (!isBlank(?p))
    FILTER (!isBlank(?d))
    """

def querybody_label():
    return """
    { ?c rdfs:label ?d }
    """
