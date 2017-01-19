from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://query.wikidata.org/sparql")

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

    wd = 'http://www.wikidata.org/entity/'
    wdt = 'http://www.wikidata.org/prop/direct/'
    p = 'http://www.wikidata.org/prop/'
    DiseaseOntologyID = 'http://www.wikidata.org/prop/direct/P699'
    ChebiID = 'http://www.wikidata.org/prop/direct/P683'
    treated_by_drug = 'http://www.wikidata.org/prop/direct/P2176'

    def dbprefix2prop(self):
        return {
            'DOID': self.DiseaseOntologyID
        }

prefix_map = PrefixMap()



def run_sparql_query(q,limit=10):
    full_sparql = "{}\n{}\nLIMIT {}".format(prefix_map.gen_header(),q,limit)
    print("FULL:"+full_sparql)
    sparql.setQuery(full_sparql)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

class UnknownPrefixException(Exception):
    pass
class InvalidIdentifierException(Exception):
    pass


def resolve_to_wikidata(id):
    """
    Given a CURIE id such as DOID:2841, return the corresponding wikidata URI(s).
    Lists are returned since some mappings may not be 1:1

    This method is reflexive - it accepts wikidata URIs, and returns input as singleton

    TODO - accept full PURLs
    """
    if id.startswith('http://www.wikidata.org'):
        return [id]
    s = id.split(':')
    if len(s) != 2:
        raise InvalidIdentifierException(id)
    [prefix, localid] = s
    p = prefix_map.dbprefix2prop()[prefix]
    results = run_sparql_query("""
    SELECT ?c WHERE {{?c <{p}> ?id .
    FILTER (?id="{doid}") }}
    """.format(p=p, doid=id))
    return [b['c']['value'] for b in results['results']['bindings']]
    
# @Deprecated
def doid_to_wikidata(id):
    results = run_sparql_query("""
    SELECT ?c WHERE {{?c DiseaseOntologyID: ?id .
    FILTER (?id="{doid}") }}
    """.format(doid=id))
    return [b['c']['value'] for b in results['results']['bindings']]

def condition_to_drug(condition_id):
    wdids = resolve_to_wikidata(condition_id)
    return flatten([wd_condition_to_drug(x) for x in wdids])

def wd_condition_to_drug(condition_id):
    results = run_sparql_query("""
    SELECT ?dc WHERE {{<{c}> treated_by_drug: ?d . ?d ChebiID: ?dc }}
    """.format(c=condition_id), limit=1000)
    # prefix IDs with CHEBI prefix
    return ['CHEBI:'+b['dc']['value'] for b in results['results']['bindings']]

def flatten(l):
    return [item for sublist in l for item in sublist]
