import SPARQLWrapper

from biolink import NAME, VERSION
from ontobio.util.user_agent import get_user_agent

USER_AGENT = get_user_agent(name=NAME, version=VERSION, modules=[SPARQLWrapper], caller_name=__name__)
sparql = SPARQLWrapper.SPARQLWrapper("http://query.wikidata.org/sparql", agent=USER_AGENT)

class PrefixMap:
    """
    Common SPARQL prefixes
    """
    def prefixes(self):
        return [attr for attr in dir(self) if not callable(getattr(self,attr)) and not attr.startswith("__")]
    def get_uri(self, pfx):
        return vars(PrefixMap).get(pfx)
    def gen_header(self):
        return "\n".join(["prefix {}: <{}>".format(attr,self.get_uri(attr)) for attr in self.prefixes()])
    
    directly_activates = 'http://purl.obolibrary.org/obo/RO_0002406'
    directly_positively_regulates = 'http://purl.obolibrary.org/obo/RO_0002629'
    enabled_by = 'http://purl.obolibrary.org/obo/RO_0002333'
    inferredG = 'http://geneontology.org/rdf/inferred/'
    contributor = 'http://purl.org/dc/elements/1.1/contributor'
    lego = 'http://geneontology.org/lego/'
    pav = 'http://purl.org/pav/providedBy/'
    json_model = 'http://geneontology.org/lego/json-model'

prefix_map = PrefixMap()

def lego_query(q,limit=10):
    full_sparql = "{}\n{}\nLIMIT {}".format(prefix_map.gen_header(),q,limit)
    print("FULL:"+full_sparql)
    sparql.setQuery(full_sparql)
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    results = sparql.query().convert()
    return results

class ModelQuery():
    """
    Query Builder for models.

    TODO: make abstract class
    TODO: evaluate alternatives e.g. https://github.com/chapmanb/bcbb/blob/master/semantic/systemsbio.py
    """
    def __init__(self, title=None, contributor=None):
        self.title=title
        self.contributor=contributor

    def gen_sparql(self):

        filters = []
        #filters.append("FILTER ?p != json_model:")  # die, json_model!

        # TODO: escape quote nastiness
        if self.title is not None:
            filters.append("FILTER regex(str(?title),'{}','i')".format(self.title))
        if self.contributor is not None:
            filters.append("FILTER regex(str(?contributor),'{}','i')".format(self.contributor))
        sparql_filter= "\n".join(filters)

        # remember, double curl braces required for interpolation
        sparql = """
        CONSTRUCT {{
        ?model dc:title ?title ;
        lego:modelstate ?modelstate ;
        dc:contributor ?contributor
        }}
        WHERE {{
        ?model a owl:Ontology ;
        dc:title ?title ;
        lego:modelstate ?modelstate .
        OPTIONAL {{ ?model pav:providedBy ?providedBy }}
        OPTIONAL {{ ?model dc:contributor ?contributor }}
        OPTIONAL {{ 
            ?inst rdfs:isDefinedBy ?model ;
                  a ?type
        }}
        {filters}
        }}
        """.format(filters=sparql_filter)
        print(sparql)
        return sparql
    
    def OLD_gen_sparql(self):

        filters = []
        #filters.append("FILTER ?p != json_model:")  # die, json_model!

        # TODO: escape quote nastiness
        if self.contributor is not None:
            filters.append("FILTER regex(?contributors,'{}','i')".format(self.contributor))
        if self.contributor is not None:
            filters.append("FILTER regex(?contributors,'{}','i')".format(self.contributor))
        sparql_filter= "\n".join(filters)
            
        sparql = """
        SELECT ?model ?title ?modelstate ?providedBy (GROUP_CONCAT(?contributor ; separator=";") as ?contributors)  WHERE 
        {{?model a owl:Ontology ; 
           dc:title ?title ;
           dc:contributor ?contributor ;
           lego:modelstate ?modelstate ;
           pav:providedBy ?providedBy
        {filters}
        }}
        GROUP BY ?model ?title ?modelstate ?providedBy""".format(filters=sparql_filter)
        
        return sparql
    
def entity_search(searchterm,
                  subclass_of=[],
                  limit=10):

    filters = []
    filters.append("FILTER regex(str(?label),'{}','i'".format(searchterm))
    for c in subclass_of:
        filters.append("FILTER ?iri rdfs:subClassOf+ {}')".format(c))

        sparql_filter= "\n".join(filters)
    sparql = """
    SELECT ?id ?label
    WHERE {{
      ?iri rdfs:label ?label
      {filters}
    }}
    """.format(filters=sparql_filter)
    return lego_query(sparql,limit)
