import logging

from flask import request
from flask_restplus import Resource, inputs
from biolink.datamodel.serializers import association
from ontobio.golr.golr_associations import map2slim
from ontobio.config import Config, get_config
from biolink.api.restplus import api
from scigraph.scigraph_util import SciGraph
from biolink import USER_AGENT

from biothings_client import get_client

log = logging.getLogger(__name__)

INVOLVED_IN = 'involved_in'
ACTS_UPSTREAM_OF_OR_WITHIN = 'acts_upstream_of_or_within'

FUNCTION_CATEGORY='function'
PHENOTYPE_CATEGORY='phenotype'
ANATOMY_CATEGORY='anatomy'

parser = api.parser()
parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387', required=True)
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID (IMPLEMENTED) or subset ID (TODO)', required=True)
parser.add_argument('exclude_automatic_assertions', type=inputs.boolean, default=False, help='If set, excludes associations that involve IEAs (ECO:0000501)')
parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
parser.add_argument('start', type=int, required=False, help='beginning row')

@api.param('relationship_type', "relationship type ('{}' or '{}')".format(INVOLVED_IN, ACTS_UPSTREAM_OF_OR_WITHIN), enum=[INVOLVED_IN, ACTS_UPSTREAM_OF_OR_WITHIN], default=ACTS_UPSTREAM_OF_OR_WITHIN)
class EntitySetFunctionSlimmer(Resource):

    function_parser = parser.copy()
    function_parser.add_argument('relationship_type', choices=[INVOLVED_IN, ACTS_UPSTREAM_OF_OR_WITHIN], default=ACTS_UPSTREAM_OF_OR_WITHIN, help="relationship type ('{}' or '{}')".format(INVOLVED_IN, ACTS_UPSTREAM_OF_OR_WITHIN))

    @api.expect(function_parser)
    def get(self):
        """
        For a given gene(s), summarize its annotations over a defined set of slim
        """
        args = self.function_parser.parse_args()
        slim = args.get('slim')
        del args['slim']
        subjects = args.get('subject')
        del args['subject']

        # Note that GO currently uses UniProt as primary ID for some sources: https://github.com/biolink/biolink-api/issues/66
        # https://github.com/monarch-initiative/dipper/issues/461

        sg_dev = SciGraph(url=get_config().scigraph_data.url)

        subjects = [x.replace('WormBase:', 'WB:') if 'WormBase:' in x else x for x in subjects]
        slimmer_subjects = []
        for s in subjects:
            if 'HGNC:' in s or 'NCBIGene:' in s or 'ENSEMBL:' in s:
                #prots = sg_dev.gene_to_uniprot_proteins(s)
                prots = gene_to_uniprot_from_mygene(s)
                if len(prots) == 0:
                    prots = [s]
                slimmer_subjects += prots
            else:
                slimmer_subjects.append(s)

        results = map2slim(
            subjects=slimmer_subjects,
            slim=slim,
            object_category='function',
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
                    if proteinId not in checked:
                        #genes = sg_dev.uniprot_protein_to_genes(proteinId)
                        genes = uniprot_to_gene_from_mygene(proteinId)
                        for gene in genes:
                            if gene.startswith('HGNC'):
                                association['subject']['id'] = gene
                                checked[proteinId] = gene
                    else:
                        association['subject']['id'] = checked[proteinId]

        return results

class EntitySetAnatomySlimmer(Resource):

    @api.expect(parser)
    def get(self):
        """
        For a given gene(s), summarize its annotations over a defined set of slim
        """
        args = parser.parse_args()
        slim = args.get('slim')
        del args['slim']
        subjects = args.get('subject')
        del args['subject']

        subjects = [x.replace('WormBase:', 'WB:') if 'WormBase:' in x else x for x in subjects]
        results = map2slim(
            subjects=subjects,
            slim=slim,
            object_category='anatomical entity',
            user_agent=USER_AGENT,
            **args
        )
        return results

class EntitySetPhenotypeSlimmer(Resource):

    @api.expect(parser)
    def get(self):
        """
        For a given gene(s), summarize its annotations over a defined set of slim
        """
        args = parser.parse_args()
        slim = args.get('slim')
        del args['slim']
        subjects = args.get('subject')
        del args['subject']

        subjects = [x.replace('WormBase:', 'WB:') if 'WormBase:' in x else x for x in subjects]
        results = map2slim(
            subjects=subjects,
            slim=slim,
            object_category='phenotype',
            user_agent=USER_AGENT,
            **args
        )
        return results

def gene_to_uniprot_from_mygene(id):
    """
    Query MyGeneInfo with a gene and get its corresponding UniProt ID
    """
    uniprot_ids = []
    mg = get_client('gene')
    try:
        results = mg.query(id, fields='uniprot')
        if results['hits']:
            for hit in results['hits']:
                if 'Swiss-Prot' in hit['uniprot']:
                    uniprot_id = hit['uniprot']['Swiss-Prot']
                    if not uniprot_id.startswith('UniProtKB'):
                        uniprot_id = "UniProtKB:{}".format(uniprot_id)
                    uniprot_ids.append(uniprot_id)
                else:
                    trembl_ids = hit['uniprot']['TrEMBL']
                    for x in trembl_ids:
                        if not x.startswith('UniProtKB'):
                            x = "UniProtKB:{}".format(x)
                        uniprot_ids.append(x)
    except ConnectionError:
        logging.error("ConnectionError while querying MyGeneInfo with {}".format(id))

    return uniprot_ids

def uniprot_to_gene_from_mygene(id):
    """
    Query MyGeneInfo with a UniProtKB id and get its corresponding HGNC gene
    """
    gene_id = None
    if id.startswith('UniProtKB'):
        id = id.split(':', 1)[1]

    mg = get_client('gene')
    try:
        results = mg.query(id, fields='HGNC')
        if results['hits']:
            hit = results['hits'][0]
            gene_id = hit['HGNC']
            if not gene_id.startswith('HGNC'):
                gene_id = 'HGNC:{}'.format(gene_id)
    except ConnectionError:
        logging.error("ConnectionError while querying MyGeneInfo with {}".format(id))

    return [gene_id]
