import logging

from flask import request
from flask_restplus import Resource
from biolink.ontology.ontology_manager import get_ontology
from biolink.datamodel.serializers import compact_association_set, association_results
from ontobio.golr.golr_associations import search_associations, GolrFields
from ontobio.ontol_factory import OntologyFactory
from ontobio.config import get_config
from ontobio.assoc_factory import AssociationSetFactory

from biolink.api.restplus import api
from biolink import USER_AGENT

log = logging.getLogger(__name__)

parser = api.parser()

parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('background', action='append', help='Entity ids in background set, e.g. NCBIGene:84570, NCBIGene:3630; used in over-representation tests')
parser.add_argument('object_category', help='E.g. phenotype, function')
parser.add_argument('subject_category', default='gene', help='Default: gene. Other types may be used e.g. disease but statistics may not make sense')
parser.add_argument('max_p_value', default='0.05', help='Exclude results with p-value greater than this')
parser.add_argument('ontology', help='ontology id. Must be obo id. Examples: go, mp, hp, uberon (optional: will be inferred if left blank)')
parser.add_argument('taxon', help='must be NCBITaxon CURIE. Example: NCBITaxon:9606')

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

        print("Loading: {}".format(ontid))
        ont = get_ontology(ontid)
        taxid = args.get('taxon')
        max_p_value = float(args.max_p_value)
        
        subjects = args.get('subject')
        background = args.get('background')
        afactory = AssociationSetFactory()
        aset = afactory.create(ontology=ont, subject_category='gene', object_category=ocat, taxon=taxid)
        enr = aset.enrichment_test(subjects=subjects, background=background, threshold=max_p_value, labels=True)
        return {'results': enr }
