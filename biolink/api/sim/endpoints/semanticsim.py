from flask_restplus import Resource
from flask import request
from ontobio.sim.api.owlsim2 import OwlSim2Api
from ontobio.sim.phenosim_engine import PhenoSimEngine
from biolink.api.restplus import api
from biolink.datamodel.sim_serializers import sim_result, compare_input

sim_engine = PhenoSimEngine(OwlSim2Api())


def get_compare_parser():

    help_msg = 'A phenotype or identifier that is composed of phenotypes (eg disease, gene)'

    sim_get_parser = api.parser()
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
    sim_search_parser = api.parser()

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
        type=int,
        required=False,
        help='ncbi taxon id'
    )
    return sim_search_parser

sim_compare_parser = get_compare_parser()
sim_search_parser = get_search_parser()


class SimSearch(Resource):

    @api.expect(sim_search_parser)
    @api.marshal_with(sim_result)
    def get(self):
        """
        Search for diseases or genes
        """
        input_args = sim_search_parser.parse_args()

        return sim_engine.search(
            id_list=input_args['id'],
            limit=input_args['limit'],
            taxon_filter=input_args['taxon']
        )


class SimCompare(Resource):

    @api.expect(compare_input)
    @api.marshal_with(sim_result)
    def post(self):
        """
        Compare a reference profile vs one or more profiles
        """
        data = request.json
        return sim_engine.compare(
            reference_ids=data['reference_ids'],
            query_profiles=data['query_ids']
        )

    @api.expect(sim_compare_parser)
    @api.marshal_with(sim_result)
    def get(self):
        """
        Compare a reference profile vs one profiles
        """
        input_args = sim_compare_parser.parse_args()

        return sim_engine.compare(
            reference_ids=input_args['ref_id'],
            query_profiles=[input_args['query_id']]
        )
