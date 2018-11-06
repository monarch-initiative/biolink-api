import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from causalmodels.lego_sparql_util import lego_query, ModelQuery

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('title', help='string to search for in title of model')
parser.add_argument('contributor', help='string to search for in contributor of model')

class ModelCollection(Resource):

    #@api.expect(parser)
    def get(self):
        """
        Returns list of ALL models
        """
        args = parser.parse_args()
        return lego_query("""
        SELECT ?x ?title ?p ?v WHERE 
        {?x a owl:Ontology ; 
           dc:title ?title ;
           ?p ?v
        FILTER(?p != json_model:)
        }""", limit=1000)

class ModelQuery(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of models matching query
        """
        args = parser.parse_args()
        mq = ModelQuery(**args)
        #if args.get('title'):
        #    mq.title = args.get('title')
        
        sparql = mq.gen_sparql()
        return lego_query(sparql, limit=100)
    
class ModelProperties(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of all properties used across all models
        """
        args = parser.parse_args()
        return lego_query("""
        SELECT DISTINCT ?p WHERE 
        {?x a owl:Ontology ; 
           ?p ?v
        FILTER(?p != json_model:)
        }""", limit=1000)

class ModelContributors(Resource):

    #@api.expect(parser)
    def get(self):
        """
        Returns list of all contributors across all models
        """
        args = parser.parse_args()
        return lego_query("""
        SELECT DISTINCT ?v WHERE 
        {?x a owl:Ontology ; 
           dc:contributor ?v
        }""", limit=1000)

class ModelInstances(Resource):

    #@api.expect(parser)
    def get(self):
        """
        Returns list of all instances
        """
        args = parser.parse_args()
        return lego_query("""
        SELECT DISTINCT ?i ?model WHERE 
        {?i rdfs:isDefinedBy ?model 
        }""", limit=1000)
    
class ModelPropertyValues(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list property-values for all models
        """
        args = parser.parse_args()
        return lego_query("""
        SELECT DISTINCT ?m ?p ?v WHERE 
        {?m a owl:Ontology ; 
           ?p ?v
        FILTER(?p != json_model:)
        }""", limit=1000)
    
class ModelObject(Resource):

    #@api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns a complete model
        """
        args = parser.parse_args()
        return lego_query("""
        CONSTRUCT { ?i ?p ?v } WHERE 
        {?i rdfs:isDefinedBy <http://model.geneontology.org/%s>; 
           ?p ?v
        }""" % id, limit=1000)

        return []

class InstanceObject(Resource):

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
    
class ActivityCollection(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of models
        """
        args = parser.parse_args()
        return lego_query("""
        SELECT ?g ?a ?type WHERE 
        {?a a <http://purl.obolibrary.org/obo/GO_0003674> .
        GRAPH ?g {?a a ?type } .
        FILTER(?g != inferredG: && ?type != owl:NamedIndividual)
        }
        """)
    
class PhysicalInteraction(Resource):

    @api.expect(parser)
    def get(self):
        """
        Returns list of models
        """
        return lego_query("""
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
    

