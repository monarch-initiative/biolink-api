__author__ = 'cjm'

import logging
import requests

# TODO: inherit a generic ResultSet model

    
class Concept:

    """
    A SG concept (payload of search)
    """

    def __init__(self, obj={}):
        self.id = obj['curie']
        self.deprecated = obj['deprecated']
        self.labels = obj['labels']
        if 'categories' in obj:
            self.category = obj['categories']
        if 'category' in obj:
            self.category = obj['category']
        self.synonyms = obj['synonyms']
        self.acronyms = obj['acronyms']
        self.abbreviations = obj['abbreviations']
        self.definitions = obj['definitions']

    def __str__(self):
        return self.id+' "'+str(str(self.labels))+'"'
    
    
    
