import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from ontobio.golr.golr_associations import map2slim
from biolink.api.restplus import api
from scigraph.scigraph_util import SciGraph
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bioentityset/slimmer', description='maps a set of entities to a slim')

parser = api.parser()
parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID (IMPLEMENTED) or subset ID (TODO)')

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
        logging.info('slimming subject is {}'.format(subjects[0]))

        subjects[0] = subjects[0].replace('WormBase:', 'WB:', 1)

        if (subjects[0].startswith('HGNC') or subjects[0].startswith('NCBIGene') or subjects[0].startswith('ENSEMBL:')):
            logging.info('swapping out {}'.format(subjects[0]))
            sg_dev = SciGraph(url='https://scigraph-data-dev.monarchinitiative.org/scigraph/')
            prots = sg_dev.gene_to_uniprot_proteins(subjects[0])
            if len(prots) == 0:
                prots = subjects
        else:
            prots = subjects

        logging.info('Looking for GO annotations to {}'.format(prots))
            results = map2slim(subjects=prots,
                               slim=slim,
                               rows=200,
                               exclude_automatic_assertions=True,
                               object_category=category,
                               **args)
        # To the fullest extent possible return HGNC ids
        for result in results:
            for association in result['assocs']:
                taxon = association['subject']['taxon']['id']
                proteinId = association['subject']['id']
                if taxon == 'NCBITaxon:9606' and proteinId.startswith('UniProtKB'):
                    sg_dev = SciGraph(url='https://scigraph-data-dev.monarchinitiative.org/scigraph/')
                    genes = sg_dev.uniprot_protein_to_genes(proteinId)
                    for gene in genes:
                        if gene.startswith('HGNC'):
                            association['subject']['id'] = gene

        return results
