import logging

from ontobio.ontol_factory import OntologyFactory
from ontobio.config import get_config

cfg = get_config()
omap = {}

def get_ontology(id):
    handle = id
    print("HANDLE={}".format(handle))
    for c in cfg.ontologies:
        print("ONT={}".format(c))
        # temporary. TODO fix
        if not isinstance(c,dict):
            if c.id == id:
                handle = c.handle
                print("Using handle={} for {}".format(handle, id))

    if handle not in omap:
        print("Creating a new ontology object for {}".format(handle))
        omap[handle] = OntologyFactory().create(handle)
    else:
        print("Using cached for {}".format(handle))
    return omap[handle]

