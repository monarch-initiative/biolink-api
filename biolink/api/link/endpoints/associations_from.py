import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from biogolr.golr_associations import get_association, search_associations
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('association', description='Associations between entities or entity and descriptors')

parser = api.parser()
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)
parser.add_argument('graphize', type=bool, help='If set, includes graph object in response')
parser.add_argument('fl_excludes_evidence', type=bool, help='If set, excludes evidence objects in response')
parser.add_argument('page', type=int, required=False, default=1, help='Page number')
parser.add_argument('rows', type=int, required=False, default=10, help='number of rows')
parser.add_argument('map_identifiers', help='Prefix to map all IDs to. E.g. NCBIGene')

parser.add_argument('subject_category', help='e.g. gene, genotype, disease')
parser.add_argument('object_category', help='e.g. disease, phenotype, gene')


@ns.route('/from/<subject>')
@api.doc(params={'subject': 'E.g. e.g. NCBIGene:84570'})
class AssociationsFrom(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject):
        """
        Returns list of matching associations
        """
        args = parser.parse_args()

        return search_associations(subject=subject, **args)

@ns.route('/to/<object>')
@api.doc(params={'object': 'E.g. e.g. MP:0013765, can also be a biological entity such as a gene'})
class AssociationsFrom(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, object):
        """
        Returns list of matching associations
        """
        args = parser.parse_args()

        return search_associations(object=object, **args)

@ns.route('/between/<subject>/<object>')
@api.doc(params={'subject': 'E.g. e.g. MGI:1342287'})
@api.doc(params={'object': 'E.g. e.g. MP:0013765, can also be a biological entity such as a gene'})
class AssociationsFrom(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject, object):
        """
        Returns list of matching associations
        """
        args = parser.parse_args()

        return search_associations(object=object, **args)
    
    

