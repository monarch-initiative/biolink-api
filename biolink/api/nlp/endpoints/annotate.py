import logging

from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association, entity_annotation_result
from biolink.api.restplus import api
from biolink.error_handlers import RouteNotImplementedException
from biolink.settings import get_biolink_config
from scigraph.scigraph_util import SciGraph
import pysolr

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('content', help='The text content to annotate')
parser.add_argument('include_category', action='append', help='Categories to include for annotation')
parser.add_argument('exclude_category', action='append', help='Categories to exclude for annotation')
parser.add_argument('min_length', default=4, help='The minimum number of characters in the annotated entity')
parser.add_argument('longest_only', type=inputs.boolean, default=False, help='Should only the longest entity be returned for an overlapping group')
parser.add_argument('include_abbreviation', type=inputs.boolean, default=False, help='Should abbreviations be included')
parser.add_argument('include_acronym', type=inputs.boolean, default=False, help='Should acronyms be included')
parser.add_argument('include_numbers', type=inputs.boolean, default=False, help='Should numbers be included')

scigraph = SciGraph(get_biolink_config()['scigraph_ontology']['url'])

def parse_args_for_annotator(parser):
    """
    Convenience method for parsing and preparing parameters for SciGraph annotator
    """
    args = parser.parse_args()
    if 'include_category' in args:
        val = args.pop('include_category')
        args['includeCat'] = val
    if 'exclude_category' in args:
        val = args.pop('exclude_category')
        args['excludeCat'] = val
    if 'min_length' in args:
        val = args.pop('min_length')
        args['minLength'] = val
    if 'longest_only' in args:
        val = args.pop('longest_only')
        args['longestOnly'] = val
    if 'include_abbreviation' in args:
        val = args.pop('include_abbreviation')
        args['include_abbrev'] = val
    if 'include_acronym' in args:
        val = args.pop('include_acronym')
        args['includeAcronym'] = val
    if 'include_acronym' in args:
        val = args.pop('include_acronym')
        args['includeAcronym'] = val
    if 'include_numbers' in args:
        val = args.pop('include_numbers')
        args['includeNumbers'] = val
    return args

class Annotate(Resource):

    @api.expect(parser)
    @api.produces(["text/plain"])
    def get(self):
        """
        Annotate a given text using SciGraph annotator
        """
        args = parse_args_for_annotator(parser)
        annotated_text = scigraph.annotate_text(http_method='get', **args)
        return annotated_text

    @api.expect(parser)
    @api.produces(["text/plain"])
    def post(self):
        """
        Annotate a given text using SciGraph annotator
        """
        args = parse_args_for_annotator(parser)
        annotated_text = scigraph.annotate_text(http_method='post', **args)
        return annotated_text

class AnnotateEntities(Resource):

    @api.expect(parser)
    @api.marshal_with(entity_annotation_result)
    def get(self):
        """
        Annotate a given content using SciGraph annotator and get all entities from content
        """
        args = parse_args_for_annotator(parser)
        results = scigraph.annotate_entities(http_method='get', **args)
        return results

    @api.expect(parser)
    @api.marshal_with(entity_annotation_result)
    def post(self):
        """
        Annotate a given content using SciGraph annotator and get all entities from content
        """
        args = parse_args_for_annotator(parser)
        results = scigraph.annotate_entities(http_method='post', **args)
        return results
