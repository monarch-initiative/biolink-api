"""
For caching it's useful to have a single instance of the owlsim(2|3)
object in biolink

This module allows us to have a singleton object by using the global
scope. Another option is to implement a singleton metaclass in ontobio.

TODO revisit this design decision as it feels wrong
possibly use https://flask.palletsprojects.com/en/2.0.x/appcontext/
"""
from ontobio.sim.api.owlsim2 import OwlSim2Api


owlsim_api = None


def get_owlsim_api():

    global owlsim_api

    if owlsim_api is None:
        owlsim_api = OwlSim2Api()

    return owlsim_api
