import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import compact_association_set, association_results
from ontobio.golr.golr_associations import search_associations, GolrFields
from ontobio.ontol_factory import OntologyFactory
from ontobio.config import get_config
from ontobio.assoc_factory import AssociationSetFactory

from biolink.api.restplus import api

log = logging.getLogger(__name__)

# TODO: handle this centrally
omap = {}

def get_ontology(id):
    handle = None 
    for c in get_config().ontologies:
        print("ONT={}".format(c))
        # temporary. TODO fix
        if not isinstance(c,dict):
            if c.id == id:
                handle = c.handle
                
    if handle not in omap:
        omap[handle] = OntologyFactory().create(handle)
    return omap[handle]

ns = api.namespace('bioentityset', description='operations over sets of entities')

parser = api.parser()

parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('background', action='append', help='Entity ids in background set, e.g. NCBIGene:84570, NCBIGene:3630; used in over-representation tests')
parser.add_argument('object_category', help='E.g. phenotype, function')
parser.add_argument('object_slim', help='Slim or subset to which the descriptors are to be mapped, NOT IMPLEMENTED')
parser.add_argument('ontology', help='ontology id. Must be obo id. Examples: go, mp, hp, uberon (optional: will be inferred if left blank)')
parser.add_argument('taxon', help='must be NCBITaxon CURIE. Example: NCBITaxon:9606')

@ns.route('/overrepresentation/')
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. function, phenotype, disease'})
class OverRepresentation(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self):
        """
        Summary statistics for objects associated
        """
        args = parser.parse_args()

        M=GolrFields()
        ont = None
        ocat = args.get('object_category')
        ontid = args.get('ontology')
        if ontid is None:
            if ocat == 'function':
                ontid = 'go'
            if ocat == 'phenotype':
                # TODO: other phenotype ontologies
                ontid = 'hp'
        ont = get_ontology(ontid)
        taxid = args.get('taxon')
        
        subjects = args.get('subject')
        background = args.get('background')
        afactory = AssociationSetFactory()
        aset = afactory.create(ontology=ont, subject_category='gene', object_category=ocat, taxon=taxid)
        enr = aset.enrichment_test(subjects=subjects, threshold=0.05, labels=True)
        return {'results':enr}

    
    

