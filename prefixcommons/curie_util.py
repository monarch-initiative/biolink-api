import json
import requests
from contextlib import closing

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
    return json.loads(jsonstr)

def read_remote_jsonld_context(url):
    """
    Returns a prefix map from a JSON-LD context from a URL

    e.g https://raw.githubusercontent.com/prefixcommons/biocontext/master/registry/monarch_context.jsonld
    """
    with closing(requests.get(url, stream=False)) as resp:
        # TODO: redirects
        if resp.status_code == 200:
            return resp.json()

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
    for cmap in cmaps:
        for (k,v) in cmap.items():
            if (uri.startswith(v)):
                return uri.replace(v, k+":")
    if strict:
        raise NoPrefix(prefix, id)
    else:
        return uri

def expand_uri(id, cmaps=default_curie_maps, strict=False):
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
