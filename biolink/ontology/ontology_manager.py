import logging

from ontobio.ontol_factory import OntologyFactory
from biolink.settings import get_biolink_config

cfg = get_biolink_config()
omap = {}

def get_ontology(id):
    handle = id
    for c in cfg['ontologies']:
        if c['id'] == id:
            logging.info("getting handle for id: {} from cfg".format(id))
            handle = c['handle']

    if handle not in omap:
        logging.info("Creating a new ontology object for {}".format(handle))
        ofa = OntologyFactory()
        omap[handle] = ofa.create(handle)
    else:
        logging.info("Using cached for {}".format(handle))
    return omap[handle]

