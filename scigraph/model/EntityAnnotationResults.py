__author__ = 'cjm'

import logging
import requests

# TODO: inherit a generic ResultSet model

class EntityAnnotationResults:

    """
    The results of a SciGraph EA call
    """

    def __init__(self, results=[], content=None):
        self.content = content
        self.spans = []
        for r in results:
            self.spans.append(Span(r, content))
        return

class Span:

    """
    A marked-up span of text
    """

    def __init__(self, obj={}, content=None):
        self.start = obj['start']
        self.end = obj['end']
        self.text = content[self.start:self.end]
        self.token = Token(obj['token'])
        return
    
    
class Token:

    """
    A marked-up span of text
    """

    def __init__(self, obj={}):
        self.id = obj['id']
        self.categories = obj['categories']
        self.terms = obj['terms']

    
    
