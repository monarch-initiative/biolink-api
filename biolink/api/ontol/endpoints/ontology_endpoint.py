import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
from causalmodels.lego_sparql_util import lego_query, ModelQuery

from ontobio.sparql.sparql_go import goSummary, goSubsets, subset
from ontobio.sparql.sparql_ontol_utils import run_sparql_on, EOntology, transform, transformArray

from ontobio.golr.golr_query import GolrSearchQuery, run_solr_on, run_solr_text_on, ESOLR, ESOLRDoc, replace

from ontobio.ontol_factory import OntologyFactory
from biolink.ontology.ontology_manager import get_ontology
from ontobio.io.ontol_renderers import OboJsonGraphRenderer

from biolink.api.entityset.endpoints.slimmer import gene_to_uniprot_from_mygene, uniprot_to_gene_from_mygene


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


        q = "*:*"
        qf = ""
        fq = "&fq=subset:" + id + "&rows=1000"
        fields = "annotation_class,annotation_class_label,description,source"

        # This is a temporary fix while waiting for the PR of the AGR slim on go-ontology
        if id == "goslim_agr":

            terms_list = set()
            for section in agr_slim_order:
                terms_list.add(section['category'])
                for term in section['terms']:
                    terms_list.add(term)

            goslim_agr_ids = "\" \"".join(terms_list)
            fq = "&fq=annotation_class:(\"" + goslim_agr_ids + "\")&rows=1000"

        data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.ONTOLOGY, q, qf, fields, fq)

        tr = {}
        for term in data:
            source = term['source']
            if source not in tr:
                tr[source] = { "annotation_class_label" : source, "terms" : [] }
            ready_term = term.copy()
            del ready_term["source"]
            tr[source]["terms"].append(ready_term)

        cats = []
        for category in tr:
            cats.append(category)

        fq = "&fq=annotation_class_label:(" + " or ".join(cats) + ")&rows=1000"
        data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.ONTOLOGY, q, qf, fields, fq)

        for category in tr:
            for temp in data:
                if temp["annotation_class_label"] == category:
                    tr[category]["annotation_class"] = temp["annotation_class"]
                    tr[category]["description"] = temp["description"]
                    break

        result = []
        for category in tr:
            cat = tr[category]
            result.append(cat)           


        # if goslim_agr, reorder the list based on the temporary json object below
        if id == "goslim_agr":
            temp = []
            for agr_category in agr_slim_order:
                cat = agr_category['category']
                for category in result:
                    if category['annotation_class'] == cat:
                        ordered_terms = []
                        for ot in agr_category['terms']:
                            for uot in category['terms']:
                                if uot['annotation_class'] == ot:
                                    ordered_terms.append(uot)
                                    break
                        category["terms"] = ordered_terms
                        temp.append(category)
            result = temp

        return result


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


ribbon_parser = api.parser()
ribbon_parser.add_argument('subset', help='Name of the subset to map GO terms (e.g. goslim_agr)')
ribbon_parser.add_argument('subject', action='append', help='List of Gene ids (e.g. MGI:98214, RGD:620474)')
ribbon_parser.add_argument('ecodes', action='append', help='List of Evidence Codes to include (e.g. EXP, IDA). Has priority over exclude_IBA')
ribbon_parser.add_argument('exclude_IBA', type=inputs.boolean, default=False, help='If true, excludes IBA annotations')
ribbon_parser.add_argument('exclude_PB', type=inputs.boolean, default=False, help='If true, excludes direct annotations to protein binding')
ribbon_parser.add_argument('cross_aspect', type=inputs.boolean, default=False, help='If true, can retrieve terms from other aspects if using a cross-aspect relationship such as regulates_closure')

class OntologyRibbons(Resource):

    aspect_map = {
        "P": "GO:0008150",
        "F": "GO:0003674",
        "C": "GO:0005575"
    }

    @api.expect(ribbon_parser)
    def get(self):
        """
        Fetch the summary of annotations for a given gene or set of genes
        """
        args = ribbon_parser.parse_args()

        exclude_IBA = args.exclude_IBA
        exclude_PB = args.exclude_PB
        ecodes = args.ecodes
        cross_aspect = args.cross_aspect

        # Step 1: create the categories
        categories = OntologySubset.get(self, args.subset)
        for category in categories:
            # category["tooltip_class_label"] = ["class", "classes"]
            # category["tooltip_annotation_label"] = ["annotation", "annotations"]

            category["groups"] = category["terms"]
            del category["terms"]

            category["id"] = category["annotation_class"]
            del category["annotation_class"]

            category["label"] = category["annotation_class_label"]
            del category["annotation_class_label"]

            for group in category["groups"]:
                group["id"] = group["annotation_class"]
                del group["annotation_class"]

                group["label"] = group["annotation_class_label"]
                del group["annotation_class_label"]

                group["type"] = "Term"
            
            category["groups"] = [{"id" : category["id"], "label" : "all " + category["label"].lower().replace("_", " "), "description" : "Represent all annotations", "type" : "All"}] + category["groups"] + [{"id" : category["id"], "label" : "other " + category["label"].lower().replace("_", " "), "description" : "Represent all annotations not mapped to a specific category", "type" : "Other"}]
        
        # Step 2: create the entities / subjects
        subject_ids = args.subject
        # print("SUBS : " , subject_ids)

        # ID conversion
        subject_ids = [x.replace('WormBase:', 'WB:') if 'WormBase:' in x else x for x in subject_ids]
        slimmer_subjects = []
        mapped_ids = { }
        reverse_mapped_ids = { }
        for s in subject_ids:
            if 'HGNC:' in s or 'NCBIGene:' in s or 'ENSEMBL:' in s:
                prots = gene_to_uniprot_from_mygene(s)
                mapped_ids[s] = prots[0]
                reverse_mapped_ids[prots[0]] = s
                if len(prots) == 0:
                    prots = [s]
                slimmer_subjects += prots
            else:
                slimmer_subjects.append(s)

        print("SLIMMER SUBS : " , slimmer_subjects)
        subject_ids = slimmer_subjects

        # should remove any undefined subject
        for subject_id in subject_ids:
            if subject_id == "undefined":
                subject_ids.remove(subject_id)

        # because of the MGI:MGI
        mod_ids = []

        subjects = []
        for subject_id in subject_ids:

            entity = { "id" : subject_id , 
                        "groups" : { },
                        "nb_classes" : 0,
                        "nb_annotations": 0,
                        "terms" : set() }

            if subject_id.startswith("MGI:"):
                subject_id = "MGI:" + subject_id
            mod_ids.append(subject_id)

            q = "*:*"
            qf = ""
            fq = "&fq=bioentity:\"" + subject_id + "\"&rows=100000"
            fields = "annotation_class,evidence_type,regulates_closure,aspect"
            if ecodes:
                fq += "&fq=evidence_type:(\"" + '" "'.join(ecodes) + "\")"
            elif exclude_IBA:
                fq += "&fq=!evidence_type:IBA"
            if exclude_PB:
                fq += "&fq=!annotation_class:\"GO:0005515\""
            data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.ANNOTATION, q, qf, fields, fq)

            # compute number of terms and annotations
            for annot in data:
                aspect = self.aspect_map[annot["aspect"]]
                found = False

                for cat in categories:

                    for gp in cat['groups']:
                        group = gp['id']

                        if gp['type'] == "Other":
                            continue

                        # only allow annotated terms belonging to the same category if cross_aspect
                        if cross_aspect or cat['id'] == aspect:

                            # is this annotation part of the current group, based on the regulates_closure ?
                            if group in annot['regulates_closure']:
                                found = True
                                break
                if found:
                    entity['terms'].add(annot['annotation_class'])
                    entity['nb_annotations'] += 1


            for cat in categories:

                for gp in cat['groups']:
                    group = gp['id']

                    if gp['type'] == "Other":
                        continue

                    for annot in data:
                        aspect = self.aspect_map[annot["aspect"]]

                        # only allow annotated terms belonging to the same category if cross_aspect
                        if cross_aspect or cat['id'] == aspect:

                            # is this annotation part of the current group, based on the regulates_closure ?
                            if group in annot['regulates_closure']:

                                # if the group has not been met yet, create it
                                if group not in entity['groups']:
                                    entity['groups'][group] = { }
                                    entity['groups'][group]['ALL'] = { "terms" : set(), "nb_classes" : 0, "nb_annotations" : 0 }

                                # if the subgroup has not been met yet, create it
                                if annot['evidence_type'] not in entity['groups'][group]:
                                    entity['groups'][group][annot['evidence_type']] = { "terms" : set(), "nb_classes" : 0, "nb_annotations" : 0 }

                                # for each annotation, add the term and increment the nb of annotations
                                entity['groups'][group][annot['evidence_type']]['terms'].add(annot['annotation_class'])
                                entity['groups'][group][annot['evidence_type']]['nb_annotations'] += 1
                                entity['groups'][group]['ALL']['terms'].add(annot['annotation_class'])
                                entity['groups'][group]['ALL']['nb_annotations'] += 1

                                # entity['terms'].add(annot['annotation_class'])
                                # entity['nb_annotations'] += 1


                other = { }
                other["ALL"] = { "terms" : set(), "nb_classes" : 0, "nb_annotations" : 0 }

                # creating list of annotations not annotated to a specific term
                not_found = set()
                for annot in data:
                    found = False
                    for gp in cat['groups']:
                        if annot['annotation_class'] == gp['id']:
                            found = True
                    if not found:    
                        not_found.add(annot['annotation_class'])

                for nf in not_found:
                    for annot in data:
                        if nf == annot['annotation_class']:
                            # print(nf, annot['annotation_class'])
                            aspect = self.aspect_map[annot["aspect"]]

                            # only allow annotated terms belonging to the same category
                            if cat['id'] == aspect:
                        
                                # if the subgroup has not been met yet, create it
                                if annot['evidence_type'] not in other:
                                    other[annot['evidence_type']] = { "terms" : set(), "nb_classes" : 0, "nb_annotations" : 0 }

                                # for each annotation, add the term and increment the nb of annotations
                                other[annot['evidence_type']]['terms'].add(annot['annotation_class'])
                                other[annot['evidence_type']]['nb_annotations'] += 1
                                other['ALL']['terms'].add(annot['annotation_class'])
                                other['ALL']['nb_annotations'] += 1
                    
                entity['groups'][cat['id'] + "-other"] = other

            # compute the number of classes for each group that have subgroup (annotations)
            for group in entity['groups']:
                for subgroup in entity['groups'][group]:
                    entity['groups'][group][subgroup]['nb_classes'] = len(entity['groups'][group][subgroup]['terms'])
                    if "-other" not in group:
                        del entity['groups'][group][subgroup]['terms']
                    else:
                        entity['groups'][group][subgroup]['terms'] = list(entity['groups'][group][subgroup]['terms'])

            entity['nb_classes'] = len(entity['terms'])
            del entity['terms']

            subjects.append(entity)

        # lastly, fill out the entity details
        q = "*:*"
        qf = ""
        fq = "&fq=bioentity:(\"" + "\" or \"".join(mod_ids) + "\")&rows=100000"
        fields = "bioentity,bioentity_label,taxon,taxon_label"
        data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.BIOENTITY, q, qf, fields, fq)

        for entity in subjects:
            for entity_detail in data:
                subject_id = entity_detail['bioentity'].replace("MGI:MGI:", "MGI:")

                if entity['id'] == subject_id:
                    entity['label'] = entity_detail['bioentity_label']
                    entity['taxon_id'] = entity_detail['taxon']
                    entity['taxon_label'] = entity_detail['taxon_label']

        # map the entity back to their original IDs
        for entity in subjects:
            if entity['id'] in reverse_mapped_ids:
                entity['id'] = reverse_mapped_ids[entity['id']]            


        # if any subject without annotation is retrieved, remove it
        to_remove = []
        for entity in subjects:
            if entity['nb_annotations'] == 0:
                to_remove.append(entity)

        for entity in to_remove:
            subjects.remove(entity)
            
            
        # http://golr-aux.geneontology.io/solr/select/?q=*:*&fq=document_category:%22bioentity%22&rows=10&wt=json&fl=bioentity,bioentity_label,taxon,taxon_label&fq=bioentity:(%22MGI:MGI:98214%22%20or%20%22RGD:620474%22)        

        result = { "categories" : categories , "subjects" : subjects }

        # print("CATEGORIES : " , categories)
        # print("SUBJECTS : " , subjects)
        return result










# this is a temporary json object, while waiting the ontology gets an annotation field to specify the order of a term in a slim
agr_slim_order = [
   { 
       "category" : "GO:0003674",
       "terms" : [
        "GO:0003824",
        "GO:0030234",
        "GO:0038023",
        "GO:0005102",
        "GO:0005215",
        "GO:0005198",
        "GO:0008092",
        "GO:0003677",
        "GO:0003723",
        "GO:0003700",
        "GO:0008134",
        "GO:0036094",
        "GO:0046872",
        "GO:0030246",
        "GO:0097367",
        "GO:0008289"
    ]
   },

    {
        "category" : "GO:0008150",
        "terms" : [
        "GO:0007049",
        "GO:0016043",
        "GO:0051234",
        "GO:0008283",
        "GO:0030154",
        "GO:0008219",
        "GO:0032502",
        "GO:0000003",
        "GO:0002376",
        "GO:0050877",
        "GO:0050896",
        "GO:0023052",
        "GO:0006259",
        "GO:0016070",
        "GO:0019538",
        "GO:0005975",
        "GO:1901135",
        "GO:0006629",
        "GO:0042592",
        "GO:0009056",
        "GO:0007610"
    ]
    },

    {
        "category" : "GO:0005575",
        "terms" : [
        "GO:0005576",
        "GO:0005886",
        "GO:0045202",
        "GO:0030054",
        "GO:0042995",
        "GO:0031410",
        "GO:0005768",
        "GO:0005773",
        "GO:0005794",
        "GO:0005783",
        "GO:0005829",
        "GO:0005739",
        "GO:0005634",
        "GO:0005694",
        "GO:0005856",
        "GO:0032991"
    ]
    }
]

