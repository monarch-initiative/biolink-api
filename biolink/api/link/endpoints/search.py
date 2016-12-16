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
parser.add_argument('object', help='Some param')

# TODO: config
golr_url = "https://solr.monarchinitiative.org/solr/golr/"
solr = pysolr.Solr(golr_url, timeout=5)

@ns.route('/')
@ns.route('/<subject_category>/')
@ns.route('/<subject_category>/<object_category>/')
##@api.doc(params={'id': 'An ID'})
class AssociationCollection(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    ##@api.marshal_list_with(association)
    def get(self, subject_category='gene', object_category='gene'):
        """
        Returns list of associations
        """
        args = parser.parse_args()

        obj_q = args.get('object')
        qmap = { 'subject_category' : subject_category, 'object_category' : 'phenotype' }
        if obj_q is not None:
            qmap['object_closure'] = obj_q
        
        
        
        qstr = " AND ".join(['{}:"{}"'.format(k,v) for (k,v) in qmap.items()])


        results = solr.search(q=qstr,
                              fl="", rows=10)

        associations = translate_docs(results)
        return associations
    
    

