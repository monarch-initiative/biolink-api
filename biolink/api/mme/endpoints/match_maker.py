from dataclasses import asdict

from flask_restplus import Resource
from flask import request, make_response
from marshmallow import ValidationError

from biolink.api.restplus import api
from biolink.api.sim.endpoints.owlsim import get_owlsim_api
from biolink.datamodel.mme_serializers import mme_request_marshmallow
from biolink.datamodel.serializers import mme

from ontobio.sim.mme import query_owlsim
from ontobio.sim.phenosim_engine import PhenoSimEngine


sim_engine = PhenoSimEngine(get_owlsim_api())


def get_mme_response(data, taxon: str = None):

    try:
        mme_request = mme_request_marshmallow.load(data)
    except ValidationError as err:
        return {
                   'error': {
                       'message': f'missing/invalid data {err}',
                       'code': 400
                   }
               }, 400

    match_data = query_owlsim(mme_request, sim_engine, taxon=taxon)
    # Filter out Nones
    match_response = asdict(match_data, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

    response = make_response(match_response)
    response.headers["Content-Type"] = "application/vnd.ga4gh.matchmaker.v1.1+json"
    return response


class DiseaseMme(Resource):

    @api.expect(mme)
    def post(self):
        """
        Match a patient to diseases based on their phenotypes
        """
        data = request.json
        return get_mme_response(data, '9606')


class MouseMme(Resource):

    @api.expect(mme)
    def post(self):
        """
        Match a patient to mouse genes based on similar phenotypes
        """
        data = request.json
        return get_mme_response(data, '10090')


class ZebrafishMme(Resource):

    @api.expect(mme)
    def post(self):
        """
        Match a patient to zebrafish genes based on similar phenotypes
        """
        data = request.json
        return get_mme_response(data, '7955')


class FlyMme(Resource):

    @api.expect(mme)
    def post(self):
        """
        Match a patient to fruit fly genes based on similar phenotypes
        """
        data = request.json
        return get_mme_response(data, '7227')


class NematodeMme(Resource):

    @api.expect(mme)
    def post(self):
        """
        Match a patient to nematode genes based on similar phenotypes
        """
        data = request.json
        return get_mme_response(data, '6239')
