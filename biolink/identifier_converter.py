import logging
from biolink.settings import get_biolink_config
from scigraph.scigraph_util import SciGraph
from biothings_client import get_client


class SciGraphIdentifierConverter(object):
    """
    Class for performing ID conversion using SciGraph
    """
    def __init__(self):
        self.scigraph = SciGraph(get_biolink_config()['scigraph_data']['url'])

    def convert_gene_to_protein(self, identifier):
        """
        Query SciGraph with a gene ID and get its corresponding UniProtKB ID
        """
        protein_ids = self.scigraph.gene_to_uniprot_proteins(identifier)
        return protein_ids

    def convert_protein_to_gene(self, identifier):
        """
        Query SciGraph with UniProtKB ID and get its corresponding HGNC gene ID
        """
        gene_ids = self.scigraph.uniprot_protein_to_genes(identifier)
        return gene_ids


class MyGeneInfoIdentifierConverter(object):
    """
    Class for performing ID conversion using MyGeneInfo
    """
    def __init__(self):
        self.mygene_client = get_client('gene')

    def convert_gene_to_protein(self, identifier):
        """
        Query MyGeneInfo with a gene ID and get its corresponding UniProtKB ID
        """
        uniprot_ids = []
        if identifier.startswith('NCBIGene:'):
            # MyGeneInfo uses 'entrezgene' prefix instead of 'NCBIGene'
            identifier = identifier.replace('NCBIGene', 'entrezgene')
        try:
            results = self.mygene_client.query(identifier, fields='uniprot')
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
            logging.error("ConnectionError while querying MyGeneInfo with {}".format(identifier))

        return uniprot_ids

    def convert_protein_to_gene(self, identifier):
        """
        Query MyGeneInfo with UniProtKB ID and get its corresponding HGNC gene ID
        """
        gene_id = None
        if identifier.startswith('UniProtKB'):
            identifier = identifier.split(':', 1)[1]

        try:
            results = self.mygene_client.query(identifier, fields='HGNC')
            if results['hits']:
                hit = results['hits'][0]
                gene_id = hit['HGNC']
                if not gene_id.startswith('HGNC'):
                    gene_id = 'HGNC:{}'.format(gene_id)
        except ConnectionError:
            logging.error("ConnectionError while querying MyGeneInfo with {}".format(identifier))

        return [gene_id]
