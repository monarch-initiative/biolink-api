import SPARQLWrapper, logging

from biolink import NAME, VERSION
from ontobio.util.user_agent import get_user_agent

USER_AGENT = get_user_agent(name=NAME, version=VERSION, modules=[SPARQLWrapper], caller_name=__name__)
sparql = SPARQLWrapper.SPARQLWrapper("http://sparql.uniprot.org/sparql", agent=USER_AGENT)

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

    up = 'http://purl.uniprot.org/core/'
    db = 'http://purl.uniprot.org/database/'

    def pmap(self):
        return {
            'uniprot': 'UniProtKB',
            'interpro': 'InterPro',
        }

prefix_map = PrefixMap()



def run_sparql_query(q,limit=10):
    full_sparql = "{}\n{}\nLIMIT {}".format(prefix_map.gen_header(),q,limit)
    logging.info("FULL:"+full_sparql)
    sparql.setQuery(full_sparql)
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    results = sparql.query().convert()
    return results

class UnknownPrefixException(Exception):
    pass
class InvalidIdentifierException(Exception):
    pass


def resolve_to_uniprot(id):
    """
    Given a CURIE id such as UniProtKB:P12345, return the corresponding UniProt URI(s).
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
    (_,is_curie,p) = prefix_map.dbprefix2prop()[prefix]
    q = id
    if not is_curie:
        q = localid
    results = run_sparql_query("""
    SELECT ?c WHERE {{?c <{p}> ?id .
    FILTER (?id="{q}") }}
    """.format(p=p, q=q))
    return [b['c']['value'] for b in results['results']['bindings']]
    

def uri_to_id(uri):
    id1 = uri.replace("http://purl.uniprot.org/","")
    [db,localid] =id1.split("/")
    pm = prefix_map.pmap()
    if db in pm:
        db = pm[db]
    return db + ":" + localid

def id_to_uri(id):
    [db,localid] =id.split(":")
    pm = prefix_map.pmap()
    for (k,v) in pm.items():
        if db == v:
            db =k
    return "http://purl.uniprot.org/{}/{}".format(db,localid)

def seeAlso(id,db=None):
    uri = id_to_uri(id)
    rs = []
    results = run_sparql_query("""
    SELECT ?o WHERE {{<{s}> rdfs:seeAlso ?o . ?o up:database db:{db} }}
    """.format(s=uri,db=db), limit=1000)
    for b in results['results']['bindings']:
        rs.append(uri_to_id(b['o']['value']))
    return rs
                


