import json
import requests
from contextlib import closing
from cachier import cachier
import datetime

SHELF_LIFE = datetime.timedelta(days=1)

class CurieError(Exception):
    """base class"""

class NoExpansion(CurieError):
    """Thrown if no prefix exists."""
    def __init__(self, prefix, id):
        self.prefix = prefix
        self.id = id

class NoContraction(CurieError):
    """Thrown if no prefix matches."""
    def __init__(self, uri):
        self.uri = uri
        
class NoPrefix(CurieError):
    """Thrown if no prefix matches."""
    def __init__(self, curie):
        self.curie = curie
        
class AmbiguousPrefix(CurieError):
    """Thrown if multiple prefix matches."""
    def __init__(self, uri, curies):
        self.uri = uri
        self.curie = curie

class InvalidSyntax(CurieError):
    """Thrown if curie does not contain ":" ."""
    def __init__(self, id):
        self.id = id


def read_local_jsonld_context(fn):
    """
    Reads a prefix map from a JSON-LD context file from local disk
    """

    f = open(fn, 'r')
    jsonstr = f.read()
    f.close()
    return extract_prefixmap(json.loads(jsonstr))

@cachier(stale_after=SHELF_LIFE)
def read_remote_jsonld_context(url):
    """
    Returns a prefix map from a JSON-LD context from a URL

    e.g https://raw.githubusercontent.com/prefixcommons/biocontext/master/registry/monarch_context.jsonld
    """
    with closing(requests.get(url, stream=False)) as resp:
        # TODO: redirects
        if resp.status_code == 200:
            return extract_prefixmap(resp.json())

def extract_prefixmap(obj):
    if '@context' in obj:
        return obj['@context']
    else:
        return obj
        
@cachier(stale_after=SHELF_LIFE)
def read_biocontext(name):
    """
    Uses prefixcommons registry

    E.g. monarch_context
    """
    return read_remote_jsonld_context("https://raw.githubusercontent.com/prefixcommons/biocontext/master/registry/"+name+".jsonld")
        

# TODO: configration
default_curie_maps = [read_biocontext('monarch_context'),read_biocontext('obo_context')]

def get_prefixes(cmaps=default_curie_maps):
    prefixes = []
    for cmap in cmaps:
        prefixes += cmap.keys()
    return prefixes
        

def contract_uri(uri, cmaps=default_curie_maps, strict=False):
    """
    Contracts a URI/IRI to a CURIE/identifier

    Returns a list of possible CURIES

    If strict is True, then exactly on result expected.

    Note if there are ambiguous rules it is possible to have multiple (e.g. GO:nnnn and OBO:GO_nnnn)
    """
    curies = []
    for cmap in cmaps:
        for (k,v) in cmap.items():
            if isinstance(v, str):
                if (uri.startswith(v)):
                    curies.append(uri.replace(v, k+":"))
    if strict:
        if len(curies) == 0:
            raise NoPrefix(uri)
        if len(curies) > 1:
            raise AmbiguousPrefix(uri, curies)
    return curies

def expand_uri(id, cmaps=default_curie_maps, strict=False):
    """
    Expands a CURIE/identifier to a URI
    """
    if id.find(":") == -1:
        if strict:
            raise InvalidSyntax(id)
        else:
            return id
    [prefix,localid] = id.split(":",1)
    for cmap in cmaps:
        if prefix in cmap:
            return cmap[prefix] + localid
    if strict:
        raise NoExpansion(prefix, id)
    else:
        return id
