import logging

from flask import request
from flask_restplus import Resource
from biolink.api.link.serializers import association
from biolink.api.restplus import api
from biolink.util.golr_associations import translate_docs
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('link/search', description='Find links')

parser = api.parser()
parser.add_argument('subject', help='SUBJECT id, e.g. NCBIGene:84570. Includes inferred by default')
parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
parser.add_argument('object', help='OBJECT id, e.g. HP:0011927. Includes inferred by default')

# TODO: config
golr_url = "https://solr.monarchinitiative.org/solr/golr/"
solr = pysolr.Solr(golr_url, timeout=5)

@ns.route('/')
@ns.route('/<subject_category>/')
@ns.route('/<subject_category>/<object_category>/')
@api.doc(params={'subject_category': 'CATEGORY of entity at link SUBJECT (source), e.g. gene, disease, genotype'})
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
class AssociationCollection(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, subject_category='gene', object_category='gene'):
        """
        Returns list of associations
        """
        args = parser.parse_args()

        sub_q = args.get('subject')
        obj_q = args.get('object')
        tax_q = args.get('subject_taxon')
        qmap = { 'subject_category' : subject_category, 'object_category' : 'phenotype' }
        if obj_q is not None:
            # TODO: make configurable whether to use closure
            qmap['object_closure'] = obj_q
        if sub_q is not None:
            qmap['subject_closure'] = sub_q
        if tax_q is not None:
            qmap['subject_taxon_closure'] = tax_q
        
        
        
        qstr = " AND ".join(['{}:"{}"'.format(k,v) for (k,v) in qmap.items()])


        results = solr.search(q=qstr,
                              fl="", rows=10)

        associations = translate_docs(results)
        return associations
    
    

