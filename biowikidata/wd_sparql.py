"""
Provide a facade over Wikidata SPARQL queries.

While this does not do anything significant beyond wrapping a SPARQL query, it provides certain conveniences:

 - mapping to and from CURIEs used in Monarch
 - providing simple to call methods for common queries

TODO:

Return objects following the biolink/OBAN association model

"""
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://query.wikidata.org/sparql")

class PrefixMap:
    """
    Common SPARQL prefixes used by wikidata.

    Note we use the "trick" whereby an entire property URI can be encoded as a prefix.
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
    UniProtID = 'http://www.wikidata.org/prop/direct/P352'
    treated_by_drug = 'http://www.wikidata.org/prop/direct/P2176'
    physically_interacts_with = 'http://www.wikidata.org/prop/direct/P129'

    def dbprefix2prop(self):
        return {
            'DOID': (True, self.DiseaseOntologyID),
            'UniProtKB': (False, self.UniProtID)
        }

prefix_map = PrefixMap()

def run_sparql_query(q,limit=10):
    """
    Run a given SPARQL query over the Wikidata SPARQL endpoint
    """
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

    # in WD, some IDs are stored as localids only (e.g. P34995 in UniProt)
    # other IDs are stored as full CURIEs (e.g. DOID)
    (is_curie,p) = prefix_map.dbprefix2prop()[prefix]
    q = id
    if not is_curie:
        q = localid
    results = run_sparql_query("""
    SELECT ?c WHERE {{?c <{p}> ?id .
    FILTER (?id="{q}") }}
    """.format(p=p, q=q))
    return [b['c']['value'] for b in results['results']['bindings']]
    
# @Deprecated
def doid_to_wikidata(id):
    results = run_sparql_query("""
    SELECT ?c WHERE {{?c DiseaseOntologyID: ?id .
    FILTER (?id="{doid}") }}
    """.format(doid=id))
    return [b['c']['value'] for b in results['results']['bindings']]

def condition_to_drug(condition_id):
    """
    Given a condition (e.g. disease) return drug used to treat it.

    Accepts CURIEs, eg. DOID:nnnn
    """
    wdids = resolve_to_wikidata(condition_id)
    return flatten([wd_condition_to_drug(x) for x in wdids])

def wd_condition_to_drug(condition_id):
    """
    Accepts WD URIs as args.

    TODO: capture everything in http://tinyurl.com/knuzgt7
    """
    results = run_sparql_query("""
    SELECT ?dc WHERE {{<{c}> treated_by_drug: ?d . ?d ChebiID: ?dc }}
    """.format(c=condition_id), limit=1000)
    # prefix IDs with CHEBI prefix
    return ['CHEBI:'+b['dc']['value'] for b in results['results']['bindings']]

# isn't there a standard python function for this?
def flatten(l):
    return [item for sublist in l for item in sublist]
