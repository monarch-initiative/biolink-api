from SPARQLWrapper import SPARQLWrapper, JSON

# TODO
ontol_sources = {
    'go': "http://rdf.geneontology.org/sparql",
    '': "http://sparql.hegroup.org/sparql"
    }

def run_sparql(q):
    # TODO: select based on ontology
    #sparql = SPARQLWrapper("http://rdf.geneontology.org/sparql")
    sparql = SPARQLWrapper("http://sparql.hegroup.org/sparql")
    
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def fetchall_isa(ont):
    """
    Ontobee uses NGs such as http://purl.obolibrary.org/obo/merged/CL
    """

    namedGraph = 'http://purl.obolibrary.org/obo/merged/' + ont.upper()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {{ ?c rdfs:subClassOf ?d }}
    }} LIMIT 10
    """.format(g=namedGraph)
    print(query)
    results = run_sparql(query)
    print(results)
    bindings = results['results']['bindings']
    return [(r['c']['value'],r['d']['value']) for r in bindings]
