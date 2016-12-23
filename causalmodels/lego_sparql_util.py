from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://rdf.geneontology.org/sparql")

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
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

class ModelQuery():
    """
    Query Builder for models.

    TODO: make abstract class
    TODO: evaluate alternatives e.g. https://github.com/chapmanb/bcbb/blob/master/semantic/systemsbio.py
    """
    def __init__(self):
        self.title=""


    def gen_sparql(self):
        
        sparql = """
        SELECT ?model ?title ?modelstate ?providedBy (GROUP_CONCAT(?contributor ; separator=";") as ?contributors)  WHERE 
        {?model a owl:Ontology ; 
           dc:title ?title ;
           dc:contributor ?contributor ;
           lego:modelstate ?modelstate ;
           pav:providedBy ?providedBy
        FILTER(?p != json_model:)
        }
        GROUP BY ?model ?title ?modelstate ?providedBy"""
        
        return sparql
    
