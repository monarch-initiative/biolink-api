import logging
from neo4j.v1 import GraphDatabase, basic_auth

# TODO: configuration via flask; see https://github.com/neo4j-examples/movies-python-bolt/blob/master/movies.py
driver = GraphDatabase.driver("bolt://neo4j.monarchinitiative.org:443")
session = driver.session()

def get_node(iri=iri):
    result = session.run("MATCH (a {iri:{iri}}) RETURN a",
                         {'iri':"http://purl.obolibrary.org/obo/HP_0000465")
    a = result[0].record["a"]
    return a

                         
