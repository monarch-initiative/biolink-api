import logging
from neo4j.v1 import GraphDatabase, basic_auth

# TODO: configuration via flask; see https://github.com/neo4j-examples/movies-python-bolt/blob/master/movies.py
driver = GraphDatabase.driver("bolt://neo4j.monarchinitiative.org:443")
session = driver.session()

def get_node(iri):
    results = session.run("MATCH (a {iri:{iri}}) RETURN a",
                         {'iri':iri})
    print(results)
    for r in results:
        print(str(r))
    return results

                         
def get_genes():
    result = session.run("MATCH (a:gene) RETURN a LIMIT 5")
    return result

                         
