import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from SPARQLWrapper import SPARQLWrapper, JSON

log = logging.getLogger(__name__)

ns = api.namespace('cam', description='Operations on causal activity models (LEGO)')

sparql = SPARQLWrapper("http://rdf.geneontology.org/sparql")

# TODO: implement cursor
def query(q):
    prefixes = """
prefix directly_activates: <http://purl.obolibrary.org/obo/RO_0002406>
prefix directly_positively_regulates: <http://purl.obolibrary.org/obo/RO_0002629>
prefix enabled_by: <http://purl.obolibrary.org/obo/RO_0002333>
prefix inferredG: <http://geneontology.org/rdf/inferred/>
"""
    sparql.setQuery(prefixes + q + " LIMIT 10")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

parser = api.parser()

@ns.route('/graph/')
class ModelCollection(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of models
        """
        args = parser.parse_args()
        sparql.setQuery("""
        SELECT ?x ?title WHERE 
        {?x a owl:Ontology ; 
           dc:title ?title
        } LIMIT 10""")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results

@ns.route('/graph/<id>')
class Model(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []

@ns.route('/instance/<id>')
class Instance(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, term):
        """
        Returns list of matches
        """
        args = parser.parse_args()

        return []
    
@ns.route('/activity/')
class ActivityCollection(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of models
        """
        args = parser.parse_args()
        return query("""
        SELECT ?g ?a ?type WHERE 
        {?a a <http://purl.obolibrary.org/obo/GO_0003674> .
        GRAPH ?g {?a a ?type } .
        FILTER(?g != inferredG: && ?type != owl:NamedIndividual)
        }
        """)
    
@ns.route('/physical_interaction/')
class PhysicalInteraction(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of models
        """
        return query("""
        SELECT * WHERE {
        GRAPH ?g {
        ?a1 enabled_by: ?m1 ;
            a ?a1cls ;
            ?arel ?a2 .
        ?a2 enabled_by: ?m2 ;
            a ?a2cls .
        ?m1 a ?m1cls .
        ?m2 a ?m2cls 
        }
        FILTER(?g != inferredG: && ?m1cls != ?m2cls && 
               ?m1cls != owl:NamedIndividual && ?m2cls != owl:NamedIndividual)
        }
        """)
    

