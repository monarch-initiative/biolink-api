import logging
import copy

from flask_restplus import Resource, inputs
from biolink.api.restplus import api
from biolink.datamodel.serializers import search_result, autocomplete_results, lay_results
from ontobio.golr.golr_query import GolrSearchQuery, GolrLayPersonSearch
from biolink import USER_AGENT

log = logging.getLogger(__name__)


def get_simple_parser():
        """
        A simple flaskrest parser object that includes basic http params
        """
        p = api.parser()
        p.add_argument('fq', action='append', required=False,
                       help='fq string passed directly to solr, note that multiple filters '
                            'will be combined with an AND operator. Combining fq_string with '
                            'other parameters may result in unexpected behavior.')
        p.add_argument('category', action='append', help='e.g. gene, disease')
        p.add_argument('prefix', action='append', help='ontology prefix: HP, -MONDO')
        p.add_argument('boost_fx', action='append', help='boost function e.g. pow(edges,0.334)')
        p.add_argument('boost_q', action='append', help='boost query e.g. category:genotype^-10')
        p.add_argument('taxon', action='append', help='taxon filter, eg NCBITaxon:9606, includes inferred taxa')
        p.add_argument('rows', type=int, required=False, default=20, help='number of rows')
        p.add_argument('start', type=str, required=False, default='0', help='row number to start from')
        p.add_argument('highlight_class', type=str, required=False, help='highlight class')
        p.add_argument('min_match', type=str, help='minimum should match parameter, see solr docs for details')
        p.add_argument('minimal_tokenizer', type=inputs.boolean, default=False,
                       help='set to true to use the minimal tokenizer, '
                            'good for variants and genotypes')
        return p


def get_advanced_parser():
        """
        Extends simple flaskrest parser object with params
        """
        p = get_simple_parser()
        p.add_argument('attribute', action='append', help='positive attributes, e.g. ontology terms, to include in query')
        p.add_argument('negative_attribute', action='append', help='negative attributes, e.g. ontology terms, to exclude in query')
        p.add_argument('weighted_attribute', action='append', help='weighted attributes, specified as a range from 0 to 1 plus an ontology term, e.g. 0.3*HP:0000001')
        p.add_argument('noise', type=inputs.boolean, default=False, help='If set, uses noise-tolerant querying, e.g owlsim, boqa')
        return p


def get_layperson_parser():
    """
    A simple flaskrest parser object that includes basic http params
    """
    p = api.parser()
    p.add_argument('rows', type=int, required=False, default=10, help='number of rows')
    p.add_argument('start', type=str, required=False, default='0', help='row number to start from')
    p.add_argument('phenotype_group', type=str, required=False, help='phenotype group id')
    p.add_argument('phenotype_group_label', type=str, required=False, help='phenotype group label')
    p.add_argument('anatomical_system', type=str, required=False, help='anatomical system id')
    p.add_argument('anatomical_system_label', type=str, required=False, help='anatomical system label')
    p.add_argument('highlight_class', type=str, required=False, help='highlight class')

    return p


def search(term, args):
    q = GolrSearchQuery(term, args)
    return q.search()
    
simple_parser = get_simple_parser()
adv_parser = get_advanced_parser()
layperson_parser = get_layperson_parser()


@api.doc(params={'term': 'search string, e.g. shh, parkinson, femur'})
class SearchEntities(Resource):

    @api.expect(simple_parser)
    @api.marshal_with(search_result)
    def get(self, term):
        """
        Returns list of matching concepts or entities using lexical search
        """
        args = simple_parser.parse_args()
        q = GolrSearchQuery(term, user_agent=USER_AGENT, **args)
        results = q.search()
        return results


@api.doc(params={'term': 'search string, e.g. muscle atrophy, frequent infections'})
class SearchHPOEntities(Resource):

    @api.expect(layperson_parser)
    @api.marshal_with(lay_results)
    def get(self, term):
        """
        Returns list of matching concepts or entities using lexical search
        """
        
        input_args = layperson_parser.parse_args()
        # params that don't directly translate to solr controller
        filtered_params = ['phenotype_group', 'phenotype_group_label',
                           'anatomical_system', 'anatomical_system_label']
        args = {k:v for k,v in input_args.items() if k not in filtered_params}

        args['fq'] = {}
        if input_args['phenotype_group'] is not None:
            args['fq']['phenotype_closure'] = input_args['phenotype_group']
        if input_args['phenotype_group_label'] is not None:
            args['fq']['phenotype_closure_label'] = input_args['phenotype_group_label']
        if input_args['anatomical_system'] is not None:
            args['fq']['anatomy_closure'] = input_args['anatomical_system']
        if input_args['anatomical_system_label'] is not None:
            args['fq']['anatomy_closure_label'] = input_args['anatomical_system_label']

        q = GolrLayPersonSearch(term, user_agent=USER_AGENT, **args)
        results = q.autocomplete()
        return results


class Autocomplete(Resource):

    @api.expect(simple_parser)
    @api.marshal_with(autocomplete_results)
    def get(self, term):
        """
        Returns list of matching concepts or entities using lexical search
        """
        args = simple_parser.parse_args()
        args['fq_string'] = copy.copy(args['fq'])
        args['fq'] = {}
        q = GolrSearchQuery(term, user_agent=USER_AGENT, **args)
        results = q.autocomplete()
        return results

#@ns.route('/entity/query/')
#class BooleanQuery(Resource):
#
#    @api.expect(adv_parser)
#    def get(self, search_term):
#        """
#        Returns list of matches based on 
#        """
#        args = parser.parse_args()
#
#        return []
