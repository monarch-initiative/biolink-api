import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association, association_results
from biolink.api.restplus import api
from ontobio.golr.golr_associations import get_association, search_associations

from biolink import USER_AGENT

log = logging.getLogger(__name__)

ns = api.namespace('association', description='Retrieve associations between entities')

parser = api.parser()
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferences by default (higher level taxa can be used)')
parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)
parser.add_argument('graphize', type=inputs.boolean, default=False, help='If set, includes graph object in response')
parser.add_argument('fl_excludes_evidence', type=inputs.boolean, default=False, help='If set, excludes evidence objects in response')
parser.add_argument('page', type=int, required=False, default=1, help='Return results starting with this row number')
parser.add_argument('rows', type=int, required=False, default=10, help='limit on number of rows')
parser.add_argument('map_identifiers', help='Prefix to map all IDs to. E.g. NCBIGene, HP, OMIM, DOID')
parser.add_argument('subject_category', help='e.g. gene, genotype, disease, function (todo: use enum)')
parser.add_argument('object_category', help='e.g. disease, phenotype, gene')
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID or subset ID')

parser.add_argument('use_compact_associations', type=inputs.boolean, default=False, help='If true, returns results in compact associations format')

@ns.route('/from/<subject>')
@api.doc(params={'subject': 'Return associations emanating from this node, e.g. specifying NCBIGene:84570 will return gene-phenotype, gene-function etc for this gene'})
class AssociationsFrom(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject):
        """
        Returns list of matching associations starting from a given subject (source)
        """
        args = parser.parse_args()

        return search_associations(subject=subject, user_agent=USER_AGENT, **args)

@ns.route('/to/<object>')
@api.doc(params={'object': 'Return associations pointing to this node. E.g. specifying MP:0013765 will return all genes, variants, strains etc annotated with this term. Can also be a biological entity such as a gene'})
class AssociationsTo(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, object):
        """
        Returns list of matching associations pointing to a given object (target)
        """
        args = parser.parse_args()

        return search_associations(object=object, user_agent=USER_AGENT, **args)

@ns.route('/between/<subject>/<object>')
@api.doc(params={'subject': 'E.g. e.g. MGI:1342287'})
@api.doc(params={'object': 'E.g. e.g. MP:0013765, can also be a biological entity such as a gene'})
class AssociationsBetween(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self, subject, object):
        """
        Returns associations connecting two entities

        Given two entities (e.g. a particular gene and a particular disease), if these two entities
        are connected (directly or indirectly), then return the association objects describing
        the connection.
        
        """
        args = parser.parse_args()
        return search_associations(object=object, user_agent=USER_AGENT, **args)
    
    

