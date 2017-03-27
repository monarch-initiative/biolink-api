from SPARQLWrapper import SPARQLWrapper, JSON
import logging

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
    UniProtID = 'http://www.wikidata.org/prop/direct/P352'
    InterProID = 'http://www.wikidata.org/prop/direct/P2926'
    has_part = 'http://www.wikidata.org/prop/direct/P527'
    treated_by_drug = 'http://www.wikidata.org/prop/direct/P2176'
    physically_interacts_with = 'http://www.wikidata.org/prop/direct/P129'

    # TODO: figure a more automated way of doing this
    # maps prefix to a tuple of (isCurie, WikidataProperty)
    def dbprefix2prop(self):
        return {
            'DOID': ('disease', True, self.DiseaseOntologyID),
            'UniProtKB': ('protein', False, self.UniProtID),
            'InterPro': ('domain', False, self.InterProID)
        }
    
    def relmap(self):
        return [
            ('disease','substance',self.treated_by_drug),
            ('protein','domain',self.has_part)
        ]

prefix_map = PrefixMap()



def run_sparql_query(q,limit=10):
    full_sparql = "{}\n{}\nLIMIT {}".format(prefix_map.gen_header(),q,limit)
    logging.info("FULL:"+full_sparql)
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
    (_,is_curie,p) = prefix_map.dbprefix2prop()[prefix]
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

def flatten(l):
    return [item for sublist in l for item in sublist]

def condition_to_drug(condition_id):
    wdids = resolve_to_wikidata(condition_id)
    return flatten([wd_condition_to_drug(x) for x in wdids])

def wd_condition_to_drug(condition_id):
    results = run_sparql_query("""
    SELECT ?dc WHERE {{<{c}> treated_by_drug: ?d . ?d ChebiID: ?dc }}
    """.format(c=condition_id), limit=1000)
    # prefix IDs with CHEBI prefix. TODO: consider more generic/metadata-driven way of doing this
    return ['CHEBI:'+b['dc']['value'] for b in results['results']['bindings']]

def protein_to_domain(protein_id):
    wdids = resolve_to_wikidata(protein_id)
    return flatten([wd_protein_to_domain(x) for x in wdids])

def wd_protein_to_domain(protein_id):
    results = run_sparql_query("""
    SELECT ?dc WHERE {{<{p}> has_part: ?d . ?d InterProID: ?dc }}
    """.format(p=protein_id), limit=1000)
    # prefix IDs. TODO: consider more generic/metadata-driven way of doing this
    return ['InterPro:'+b['dc']['value'] for b in results['results']['bindings']]

def neighbors(id,**args):
    wdids = resolve_to_wikidata(id)
    return flatten([wd_neighbors(x,**args) for x in wdids])
def wd_neighbors(id,subject_category=None,object_category=None):
    logging.info("Q: {} {} -> {}".format(id, subject_category, object_category))
    assocs = []
    for (scat,ocat,pred) in prefix_map.relmap():        
        if subject_category == scat and object_category == ocat:
            for (prefix,(cat,is_curie,idp)) in prefix_map.dbprefix2prop().items():
                logging.info("YO: {} tcat:{} {} -> {}".format(pred, cat, subject_category, object_category))            
                if cat == object_category:
                    results = run_sparql_query("""
                    SELECT ?o WHERE {{<{s}> <{p}> ?z . ?z <{idp}> ?o }}
                    """.format(s=id,p=pred,idp=idp), limit=1000)
                    for b in results['results']['bindings']:
                        obj = b['o']['value']
                        if not is_curie:
                            obj = prefix + ':' + obj
                        assocs.append({'object':obj})
    return assocs
                


