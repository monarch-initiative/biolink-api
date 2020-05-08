from flask_restplus import Resource, inputs
from flask import request
from ontobio.sim.api.owlsim2 import OwlSim2Api
from ontobio.sim.phenosim_engine import PhenoSimEngine
from ontobio.vocabulary.similarity import SimAlgorithm
from biolink.api.restplus import api
from biolink.api.sim.endpoints.owlsim import get_owlsim_api
from biolink.datamodel.sim_serializers import sim_result, compare_input

metrics = [matcher.value for matcher in OwlSim2Api.matchers()]

# Common args
sim_parser = api.parser()
sim_parser.add_argument(
        'is_feature_set',
        type=inputs.boolean,
        help='set to true if *all* input ids are phenotypic features, else set to false',
        default=True
    )

sim_parser.add_argument(
    'metric', type=str, choices=metrics,
    default='phenodigm', help='Metric for computing similarity')


def get_compare_parser():

    help_msg = 'A phenotype or identifier that is composed of phenotypes (eg disease, gene)'

    sim_get_parser = sim_parser.copy()
    sim_get_parser.add_argument(
        'ref_id',
        action='append',
        help=help_msg,
        default=[]
    )
    sim_get_parser.add_argument(
        'query_id',
        action='append',
        help=help_msg,
        default=[]
    )
    return sim_get_parser


def get_search_parser():
    sim_search_parser = sim_parser.copy()

    sim_search_parser.add_argument(
        'id',
        action='append',
        help='A phenotype or identifier that is composed of phenotypes (eg disease, gene)',
        default=[]
    )
    sim_search_parser.add_argument(
        'limit',
        type=int,
        required=False,
        default=100,
        help='number of rows'
    )
    sim_search_parser.add_argument(
        'taxon',
        type=str,
        required=False,
        help='ncbi taxon id'
    )
    return sim_search_parser

sim_compare_parser = get_compare_parser()
sim_search_parser = get_search_parser()


class SimSearch(Resource):

    sim_engine = PhenoSimEngine(get_owlsim_api())

    @api.expect(sim_search_parser)
    @api.marshal_with(sim_result)
    def get(self):
        """
        Search for phenotypically similar diseases or model genes
        """
        input_args = sim_search_parser.parse_args()

        return SimCompare.sim_engine.search(
            id_list=input_args['id'],
            limit=input_args['limit'],
            taxon_filter=input_args['taxon'],
            method=SimAlgorithm(input_args['metric']),
            is_feature_set=input_args['is_feature_set']
        )


class SimCompare(Resource):

    sim_engine = PhenoSimEngine(get_owlsim_api())

    @api.expect(compare_input)
    @api.marshal_with(sim_result)
    def post(self):
        """
        Compare a reference profile vs one or more profiles
        """
        data = request.json
        if 'metric' not in data:
            data['metric'] = 'phenodigm'

        if 'is_feature_set' not in data:
            data['is_feature_set'] = True

        return SimCompare.sim_engine.compare(
            reference_ids=data['reference_ids'],
            query_profiles=data['query_ids'],
            method=SimAlgorithm(data['metric']),
            is_feature_set=data['is_feature_set']
        )

    @api.expect(sim_compare_parser)
    @api.marshal_with(sim_result)
    def get(self):
        """
        Compare a reference profile vs one profiles
        """
        input_args = sim_compare_parser.parse_args()

        return SimCompare.sim_engine.compare(
            reference_ids=input_args['ref_id'],
            query_profiles=[input_args['query_id']],
            method=SimAlgorithm(input_args['metric']),
            is_feature_set = input_args['is_feature_set']
        )
