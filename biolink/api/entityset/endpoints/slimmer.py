import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association
from ontobio.golr.golr_associations import map2slim
from biolink.api.restplus import api
from scigraph.scigraph_util import SciGraph
from biolink import USER_AGENT

log = logging.getLogger(__name__)

ns = api.namespace('bioentityset/slimmer', description='maps a set of entities to a slim')

INVOLVED_IN = 'involved_in'
ACTS_UPSTREAM_OF_OR_WITHIN = 'acts_upstream_of_or_within'

parser = api.parser()
parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID (IMPLEMENTED) or subset ID (TODO)')
parser.add_argument('exclude_automatic_assertions', type=inputs.boolean, default=False, help='If set, excludes associations that involve IEAs (ECO:0000501)')
parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
parser.add_argument('start', type=int, required=False, help='beginning row')
parser.add_argument('relationship_type', choices=[INVOLVED_IN, ACTS_UPSTREAM_OF_OR_WITHIN], default=ACTS_UPSTREAM_OF_OR_WITHIN, help="relationship type ('{}' or '{}')".format(INVOLVED_IN, ACTS_UPSTREAM_OF_OR_WITHIN))

@ns.route('/<category>')
class EntitySetSlimmer(Resource):

    @api.expect(parser)
    def get(self, category):
        """
        Summarize a set of objects
        """
        args = parser.parse_args()
        slim = args.get('slim')
        del args['slim']
        subjects = args.get('subject')
        del args['subject']
        # Note that GO currently uses UniProt as primary ID for some sources: https://github.com/biolink/biolink-api/issues/66
        # https://github.com/monarch-initiative/dipper/issues/461
        # nota bene:
        # currently incomplete because code is not checking for the possibility of >1 subjects

        subjects[0] = subjects[0].replace('WormBase:', 'WB:', 1)
        prots = None
        if category == 'function':
            # get proteins for a gene only when the category is 'function'
            if (subjects[0].startswith('HGNC') or subjects[0].startswith('NCBIGene') or subjects[0].startswith('ENSEMBL:')):
                sg_dev = SciGraph(url='https://scigraph-data-dev.monarchinitiative.org/scigraph/')
                prots = sg_dev.gene_to_uniprot_proteins(subjects[0])
                if len(prots) == 0:
                    prots = subjects

        if prots is None:
            prots = subjects

        results = map2slim(
            subjects=prots,
            slim=slim,
            object_category=category,
            user_agent=USER_AGENT,
            **args
        )
        # To the fullest extent possible return HGNC ids
        checked = {}
        for result in results:
            for association in result['assocs']:
                taxon = association['subject']['taxon']['id']
                proteinId = association['subject']['id']
                if taxon == 'NCBITaxon:9606' and proteinId.startswith('UniProtKB:'):
                    if checked.get(proteinId) == None:
                        sg_dev = SciGraph(url='https://scigraph-data-dev.monarchinitiative.org/scigraph/')
                        genes = sg_dev.uniprot_protein_to_genes(proteinId)
                        for gene in genes:
                            if gene.startswith('HGNC'):
                                association['subject']['id'] = gene
                                checked[proteinId] = gene
                    else:
                        association['subject']['id'] = checked[proteinId]
        return results
