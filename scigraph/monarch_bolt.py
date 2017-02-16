import logging
from neo4j.v1 import GraphDatabase, basic_auth

# TODO: configuration via flask; see https://github.com/neo4j-examples/movies-python-bolt/blob/master/movies.py
driver = GraphDatabase.driver("bolt://neo4j.monarchinitiative.org:443")
session = driver.session()

def get_node(iri):
    results = session.run("MATCH (a:Node {iri:{iri}}) RETURN a",
                         {'iri':iri})

    print("RESULTS="+str(results))
    n = None
    for r in results:
        print("R="+str(r))
        n = r
    return n

                         
