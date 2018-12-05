import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from causalmodels.lego_sparql_util import lego_query, ModelQuery

from ontobio.sparql.sparql_go import goSummary, goSubsets, subset
from ontobio.sparql.sparql_ontol_utils import run_sparql_on, EOntology, transform, transformArray

from ontobio.golr.golr_query import GolrSearchQuery, run_solr_on, ESOLR, ESOLRDoc, replace

from ontobio.ontol_factory import OntologyFactory
from biolink.ontology.ontology_manager import get_ontology
from ontobio.io.ontol_renderers import OboJsonGraphRenderer

import json


### Some query parameters & parsers
IS_A = "isa"
IS_A_PART_OF = "isa_partof"
REGULATES = "regulates"

related_params = api.parser()
related_params.add_argument('relationship_type', choices=[IS_A, IS_A_PART_OF, REGULATES], default=IS_A_PART_OF, help="relationship type ('{}', '{}' or '{}')".format(IS_A, IS_A_PART_OF, REGULATES))

TOPOLOGY = "topology_graph"
REGULATES_TRANSITIVITY = "regulates_transitivity_graph"
NEIGHBORHOOD_GRAPH = "neighborhood_graph"
NEIGHBORHOOD_LIMITED_GRAPH = "neighborhood_limited_graph"
graph_params = api.parser()
graph_params.add_argument('graph_type', choices=[TOPOLOGY, REGULATES_TRANSITIVITY, NEIGHBORHOOD_GRAPH, NEIGHBORHOOD_LIMITED_GRAPH], default=TOPOLOGY, help="graph type ('{}', '{}' or '{}')".format(TOPOLOGY, REGULATES_TRANSITIVITY, NEIGHBORHOOD_GRAPH, NEIGHBORHOOD_LIMITED_GRAPH))


subgraph_params = api.parser()
subgraph_params.add_argument('cnode', action='append', help='Additional classes')
subgraph_params.add_argument('include_ancestors', type=inputs.boolean, default=True, help='Include Ancestors')
subgraph_params.add_argument('include_descendants', type=inputs.boolean, help='Include Descendants')
subgraph_params.add_argument('relation', action='append', default=['subClassOf', 'BFO:0000050'], help='Additional classes')
subgraph_params.add_argument('include_meta', type=inputs.boolean, default=False, help='Include metadata in response')

### END


log = logging.getLogger(__name__)

@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0003677'})
class OntologyTerm(Resource):

    def get(self, id):
        """
        Returns meta data of an ontology term
        """
        query = goSummary(self, id)
        results = run_sparql_on(query, EOntology.GO)
        return transform(results[0], ['synonyms', 'relatedSynonyms', 'alternativeIds', 'xrefs', 'subsets'])

@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0000981'})
class OntologyTermGraph(Resource):

    @api.expect(graph_params)
    def get(self, id):
        """
        Returns graph of an ontology term
        """

        args = graph_params.parse_args()
        graph_type = args['graph_type'] + "_json" # GOLR field names

        data = run_solr_on(ESOLR.GOLR, ESOLRDoc.ONTOLOGY, id, graph_type)
        # step required as these graphs are stringified in the json
        data[graph_type] = json.loads(data[graph_type]) 
        
        return data

# @ns.route('/term/<id>/ancestor')
# class OntologyTermAncestor(Resource):

#     def get(self, id):
#         """
#         Returns ancestors of an ontology term
#         """
#         return None

# @ns.route('/term/<id>/descendant')
# class OntologyTermDescendant(Resource):

#     def get(self, id):
#         """
#         Returns descendants of an ontology term
#         """

#         ont = get_ontology("go")
#         print("ONT: ", ont)
#         print("GRAPH: ", ont.get_graph())

#         return None

@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0007275'})
class OntologyTermSubgraph(Resource):

    @api.expect(subgraph_params)
    def get(self, id):
        """
        Extract a subgraph from an ontology term
        """
        args = subgraph_params.parse_args()
        qnodes = [id]
        if args.cnode is not None:
            qnodes += args.cnode

        # COMMENT: based on the CURIE of the id, we should be able to find out the ontology automatically
        ont = get_ontology("go")
        relations = args.relation
        print("Traversing: {} using {}".format(qnodes,relations))
        nodes = ont.traverse_nodes(qnodes,
                                   up=args.include_ancestors,
                                   down=args.include_descendants,
                                   relations=relations)

        subont = ont.subontology(nodes, relations=relations)
        # TODO: meta is included regardless of whether include_meta is True or False
        ojr = OboJsonGraphRenderer(include_meta=args.include_meta)
        json_obj = ojr.to_json(subont, include_meta=args.include_meta)
        return json_obj

@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0006259'})
class OntologyTermSubsets(Resource):

    def get(self, id):
        """
        Returns subsets (slims) associated to an ontology term
        """
        query = goSubsets(self, id)
        results = run_sparql_on(query, EOntology.GO)
        results = transformArray(results, [])
        results = replace(results, "subset", "OBO:go#", "")
        return results

@api.doc(params={'id': 'name of a slim subset, e.g. goslim_agr, goslim_generic'})
class OntologySubset(Resource):

    def get(self, id):
        """
        Returns meta data of an ontology subset (slim)
        """

        query = subset(self, id)
        results = run_sparql_on(query, EOntology.GO)
        return transformArray(results, [])


# @ns.route('/term/<id>/related')
# @api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0030182'})
# class OntologyTermsRelated(Resource):

#     @api.expect(related_params)
#     def get(self, id):
#         """
#         Returns related ontology terms based on a given relationship type
#         """
#         args = related_params.parse_args()
#         relationship = args['relationship_type']

#         closure = relationship + "_closure"
#         closure_label = relationship + "_closure_label"

#         data = run_solr_on(ESOLR.GOLR, ESOLRDoc.ONTOLOGY, id, closure + "," + closure_label)
#         data = mergeWithLabels(data, closure, "goid", closure_label, "label")

#         # args = {
#         #     "q": "*:*",
#         #     "fq": "id:\"" + id + "\"",
#         #     "url": "http://golr-aux.geneontology.io/solr/",
#         #     "category": "ontology_class"
#         # }
#         # print(args)

#         # GolrSearchQuery(term=id, category="ontology_class", url="http://golr-aux.geneontology.io/solr/", fq="id:\"" + id + "\"")
#         # q = GolrSearchQuery(id, args)
#         # print("QUERY RESYLT: " , q.search())
#         return data


# @ns.route('/relation/<subject>/<object>')
# @api.doc(params={'subject': 'CURIE identifier of a GO term, e.g. GO:0006259',
#                  'object': 'CURIE identifier of a GO term, e.g. GO:0046483' })
# class OntologyTermsRelation(Resource):

#     def get(self, subject, object):
#         """
#         Returns relations between two ontology terms
#         """
#         return None

@api.doc(params={'subject': 'CURIE identifier of a GO term, e.g. GO:0006259',
                 'object': 'CURIE identifier of a GO term, e.g. GO:0046483' })
class OntologyTermsSharedAncestor(Resource):

    def get(self, subject, object):
        """
        Returns the ancestor ontology terms shared by two ontology terms
        """

        fields = "isa_partof_closure,isa_partof_closure_label"

        subres = run_solr_on(ESOLR.GOLR, ESOLRDoc.ONTOLOGY, subject, fields)
        objres = run_solr_on(ESOLR.GOLR, ESOLRDoc.ONTOLOGY, object, fields)
        
        print("SUBJECT: ", subres)
        print("OBJECT: ", objres)

        shared = []
        sharedLabels = []
        for i in range(0, len(subres['isa_partof_closure'])):
            sub = subres['isa_partof_closure'][i]
            found = False
            if sub in objres['isa_partof_closure']:
                found = True
            if found:
                shared.append(sub)
                sharedLabels.append(subres['isa_partof_closure_label'][i])
        return { "goids" : shared, "gonames: " : sharedLabels }



