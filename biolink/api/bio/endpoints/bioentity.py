import logging

from flask import request
from flask_restplus import Resource, inputs, marshal
from biolink.datamodel.serializers import node, named_object, bio_object,\
    association_results, association, disease_object, d2p_association_results
from biolink.api.restplus import api
from ontobio.golr.golr_associations import search_associations, select_distinct_subjects
from scigraph.scigraph_util import SciGraph
from biowikidata.wd_sparql import condition_to_drug
from ontobio.vocabulary.relations import HomologyTypes
from ..closure_bins import create_closure_bin
from ..association_counts import get_association_counts
from biolink import USER_AGENT

from biolink.settings import get_biolink_config, get_identifier_converter
from biolink.error_handlers import NoResultFoundException, UnhandledException, UnrecognizedBioentityTypeException

from ontobio.golr.golr_query import run_solr_text_on, ESOLR, ESOLRDoc, replace
from ontobio.config import get_config


log = logging.getLogger(__name__)

basic_parser = api.parser()
basic_parser.add_argument('start', type=int, required=False, default=0, help='beginning row')
basic_parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
basic_parser.add_argument('evidence', action='append', help='Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default) or a specific publication or other supporting object, e.g. ZFIN:ZDB-PUB-060503-2')


core_parser = api.parser()
core_parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
core_parser.add_argument('start', type=int, required=False, help='beginning row')
core_parser.add_argument('facet', type=inputs.boolean, required=False, default=False, help='Enable faceting')
core_parser.add_argument('facet_fields', action='append', default=None, required=False, help='Fields to facet on')
core_parser.add_argument('unselect_evidence', type=inputs.boolean, default=False, help='If true, excludes evidence objects in response')
core_parser.add_argument('exclude_automatic_assertions', type=inputs.boolean, default=False, help='If true, excludes associations that involve IEAs (ECO:0000501)')
core_parser.add_argument('fetch_objects', type=inputs.boolean, default=False, help='If true, returns a distinct set of association.objects (typically ontology terms). This appears at the top level of the results payload')
core_parser.add_argument('use_compact_associations', type=inputs.boolean, default=False, help='If true, returns results in compact associations format')
core_parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID or subset ID')
core_parser.add_argument('evidence', help='Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default) or a specific publication or other supporting object, e.g. ZFIN:ZDB-PUB-060503-2')
core_parser.add_argument('direct', type=inputs.boolean, default=False,
                         help='Set true to only include direct associations, and '
                              'false to include inferred (via subclass or '
                              'subclass|part of), default=False')


INVOLVED_IN = 'involved_in'
INVOLVED_IN_REGULATION_OF = 'involved_in_regulation_of'
ACTS_UPSTREAM_OF_OR_WITHIN = 'acts_upstream_of_or_within'
TYPE_GENE = 'gene'
TYPE_VARIANT = 'variant'
TYPE_GENOTYPE = 'genotype'
TYPE_PHENOTYPE = 'phenotype'
TYPE_DISEASE = 'disease'
TYPE_GOTERM = 'goterm'
TYPE_PATHWAY = 'pathway'
TYPE_ANATOMY = 'anatomy'
TYPE_SUBSTANCE = 'substance'
TYPE_INDIVIDUAL = 'individual'
TYPE_PUBLICATION = 'publication'
TYPE_MODEL = 'model'
TYPE_CASE = 'case'

categories = [TYPE_GENE, TYPE_VARIANT, TYPE_GENOTYPE,
              TYPE_PHENOTYPE, TYPE_DISEASE, TYPE_GOTERM,
              TYPE_PATHWAY, TYPE_ANATOMY, TYPE_SUBSTANCE,
              TYPE_INDIVIDUAL, TYPE_PUBLICATION, TYPE_MODEL,
              TYPE_CASE]

homolog_parser = core_parser.copy()
homolog_parser.add_argument('taxon', action='append',
                            help='Taxon CURIE of homolog, e.g. NCBITaxon:9606 (Can be an ancestral '
                                 'node in the ontology; includes inferred associations by default)')
homolog_parser.add_argument('homology_type', choices=['P', 'O', 'LDO'],
                            help='P (paralog), O (Ortholog) or LDO (least-diverged ortholog)')
homolog_parser.add_argument('direct_taxon', type=inputs.boolean, default=False,
                                      help='Set true to exclude inferred taxa')

core_parser_with_filters = core_parser.copy()
core_parser_with_filters.add_argument('taxon', action='append',
                                      help='One or more taxon CURIE to filter associations by subject '
                                           'taxon; includes inferred associations by default')
core_parser_with_filters.add_argument('direct_taxon', type=inputs.boolean, default=False,
                                      help='Set true to exclude inferred taxa')
core_parser_with_filters.add_argument('relation', help='A relation CURIE to filter associations', default=None)
core_parser_with_filters.add_argument('sort', type=str, required=False, default=None, help="Sorting responses <field> <desc,asc>")
core_parser_with_filters.add_argument('q', type=str, required=False, default=None, help="Query string to filter documents")


gene_disease_parser = core_parser_with_filters.copy()
gene_disease_parser.add_argument(
    'association_type', type=str, choices=('causal', 'non_causal', 'both'),
    default='both', help='Additional filters: causal, non_causal, both')

scigraph = SciGraph(get_biolink_config()['scigraph_data']['url'])

homol_rel = HomologyTypes.Homolog.value

identifier_converter = get_identifier_converter()

@api.doc(params={'id': 'id, e.g. NCBIGene:84570'})
class GenericObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on object of any type
        """
        args = core_parser.parse_args()
        obj = scigraph.bioobject(id)
        return obj

@api.param('id', 'id, e.g. NCBIGene:84570')
@api.param('type', 'bioentity type', enum=categories)
class GenericObjectByType(Resource):

    parser = core_parser.copy()
    parser.add_argument('get_association_counts', help='Get association counts', type=inputs.boolean, default=False)
    parser.add_argument('distinct_counts', help='Get distinct counts for associations (to be used in conjunction with \'get_association_counts\' parameter)', type=inputs.boolean, default=False)

    @api.expect(parser)
    def get(self, id, type):
        """
        Return basic info on an object for a given type
        """
        ret_val = None
        args = self.parser.parse_args()

        if type not in categories:
            raise UnrecognizedBioentityTypeException("{} is not a valid Bioentity type".format(type))

        if type == TYPE_DISEASE:
            bio_entity = scigraph.bioobject(id, type)
            ret_val = marshal(bio_entity, disease_object), 200
        else:
            bio_entity = scigraph.bioobject(id, type)
            ret_val = marshal(bio_entity, bio_object), 200
        if args['get_association_counts']:
            # *_ortholog_closure requires clique leader, so use
            # bio_entity.id instead of incoming id
            ret_val[0]['association_counts'] = get_association_counts(bio_entity.id, type, distinct_counts=args['distinct_counts'])
        return ret_val


class GenericAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns associations for an entity regardless of the type
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject=id,
            user_agent=USER_AGENT,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            **args
        )

@api.doc(params={'id': 'id, e.g. NCBIGene:3630. Equivalent IDs can be used with same results'})
class GeneInteractions(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns interactions for a gene
        """
        args = core_parser_with_filters.parse_args()

        return search_associations(
            association_type='gene_interaction',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'id, e.g. NCBIGene:3630. Equivalent IDs can be used with same results'})
class GeneHomologAssociations(Resource):

    @api.expect(homolog_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns homologs for a gene
        """
        """
        Horrible hacks
        """
        id = id.replace('WB:', 'WormBase:', 1)
        id = id.replace('WormBaseGene', 'WBGene', 1)

        logging.info("looking for homologs to {}".format(id))

        homolog_args = homolog_parser.parse_args()
        return search_associations(
            association_type='gene_homology',
            subject=id,
            object_taxon=homolog_args.taxon,
            object_taxon_direct=homolog_args.direct_taxon,
            user_agent=USER_AGENT,
            **homolog_args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GenePhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with gene
        """
        args = core_parser_with_filters.parse_args()
        results = search_associations(
            subject_category='gene',
            object_category='phenotype',
            subject=id,
            facet_limit=100000,
            user_agent=USER_AGENT,
            **args
        )

        fcs = results.get('facet_counts')
        if fcs:
            closure_bin, slim_facet = create_closure_bin(fcs.get('object_closure'))
            fcs['closure_bin'] = closure_bin
            fcs['object_closure'] = slim_facet

        return results

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GeneDiseaseAssociations(Resource):

    @api.expect(gene_disease_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with gene
        """
        args = gene_disease_parser.parse_args()
        if args['association_type'] == 'causal':
            args['association_type'] = 'gene_disease'
        elif args['association_type'] == 'non_causal':
            args['association_type'] = 'marker_disease'
        else:
            args['association_type'] = ['gene_disease', 'marker_disease']

        return search_associations(
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:50846. Equivalent IDs can be used with same results'})
class GenePathwayAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns pathways associated with gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='pathway',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GeneExpressionAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns expression events for a gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='anatomical entity',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:13434'})
class GeneAnatomyAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns anatomical entities associated with a gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='anatomical entity',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. ZFIN:ZDB-GENE-980526-166'})
class GeneGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='genotype',
            invert_subject_object=True,
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'id, e.g. NCBIGene:6469. Equivalent IDs can be used with same results'})
class GeneFunctionAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns function associations for a gene.

        IMPLEMENTATION DETAILS
        ----------------------

        Note: currently this is implemented as a query to the GO/AmiGO solr instance.
        This directly supports IDs such as:

         - ZFIN e.g. ZFIN:ZDB-GENE-050417-357

        Note that the AmiGO GOlr natively stores MGI annotations to MGI:MGI:nn. However,
        the standard for biolink is MGI:nnnn, so you should use this (will be transparently
        mapped to legacy ID)

        Additionally, for some species such as Human, GO has the annotation attached to the UniProt ID.
        Again, this should be transparently handled; e.g. you can use NCBIGene:6469, and this will be
        mapped behind the scenes for querying.
        """

        assocs = search_associations(
            object_category='function',
            subject=id,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

        # If there are no associations for the given ID, try other IDs.
        # Note the AmiGO instance does *not* support equivalent IDs
        if len(assocs['associations']) == 0:
            # Note that GO currently uses UniProt as primary ID for some sources: https://github.com/biolink/biolink-api/issues/66
            # https://github.com/monarch-initiative/dipper/issues/461
            prots = identifier_converter.convert_gene_to_protein(id)
            for prot in prots:
                pr_assocs = search_associations(
                    object_category='function',
                    subject=prot,
                    user_agent=USER_AGENT,
                    **core_parser.parse_args()
                )
                assocs = pr_assocs
        return assocs

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750'})
class GenePublicationAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns publications associated with a gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='publication',
            invert_subject_object=True,
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:17988'})
class GeneModelAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns models associated with a gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='model',
            invert_subject_object=True,
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750'})
class GeneOrthologPhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """

        Return phenotypes associated with orthologs for a gene
        """
        args = core_parser_with_filters.parse_args()
        # Get the clique leader
        gene = scigraph.get_clique_leader(id)

        filters = {
            'subject_ortholog_closure': gene.id,
        }
        if args.taxon is not None:
            filters['subject_taxon_closure'] = args.taxon

        return search_associations(
            fq=filters,
            object_category='phenotype',
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )


@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750'})
class GeneOrthologDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Return diseases associated with orthologs of a gene
        """
        args = core_parser_with_filters.parse_args()

        # Get the clique leader
        gene = scigraph.get_clique_leader(id)

        filters = {
            'subject_ortholog_closure': gene.id,
        }
        if args.taxon is not None:
            filters['subject_taxon_closure'] = args.taxon

        return search_associations(
            fq=filters,
            object_category='disease',
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. HGNC:10896'})
class GeneVariantAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns variants associated with a gene
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='gene',
            object_category='variant',
            invert_subject_object=True,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of gene, e.g. HGNC:613, HGNC:11025'})
class GeneCaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns cases associated with a gene
        """
        return search_associations(
            subject_category='gene',
            object_category='case',
            invert_subject_object=True,
            subject=id,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, Orphanet:1934, DOID:678. Equivalent IDs can be used with same results'})
class DiseasePhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(d2p_association_results)
    def get(self, id):
        """
        Returns phenotypes associated with disease
        """
        args = core_parser_with_filters.parse_args()
        results = search_associations(
            subject_category='disease',
            object_category='phenotype',
            subject=id,
            subject_direct=args.direct,
            object_direct=args.direct,
            facet_limit=100000,
            user_agent=USER_AGENT,
            **args
        )
        fcs = results.get('facet_counts')
        if fcs:
            closure_bin, slim_facet = create_closure_bin(fcs.get('object_closure'))
            fcs['closure_bin'] = closure_bin
            fcs['object_closure'] = slim_facet
        return results

@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseGeneAssociations(Resource):

    @api.expect(gene_disease_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a disease
        """
        args = gene_disease_parser.parse_args()
        if args['association_type'] == 'causal':
            args['association_type'] = 'gene_disease'
        elif args['association_type'] == 'non_causal':
            args['association_type'] = 'marker_disease'
        else:
            args['association_type'] = ['gene_disease', 'marker_disease']

        return search_associations(
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )


@api.doc(params={'id': 'CURIE identifier of disease, e.g. DOID:2841 (asthma). Equivalent IDs not yet supported'})
class DiseaseSubstanceAssociations(Resource):

    @api.expect(core_parser)
    #TODO: @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns substances associated with a disease.

        e.g. drugs or small molecules used to treat

        """
        return condition_to_drug(id)

@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseModelAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """Returns associations to models of the disease

        In the association object returned, the subject will be the disease, and the object will be the model.
        The model may be a gene or genetic element.

        If the query disease is a general class, the association subject may be to a specific disease.

        In some cases the association will be *direct*, for example if a paper asserts a genotype is a model of a disease.

        In other cases, the association will be *indirect*, for
        example, chaining over orthology. In these cases the chain
        will be reflected in the *evidence graph*

        * TODO: provide hook into owlsim for dynamic computation of models by similarity

        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='model',
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
@api.doc(params={'taxon': 'CURIE of organism taxonomy class to constrain models, e.g NCBITaxon:10090 (M. musculus).\n\n Higher level taxa may be used'})
@api.deprecated
class DiseaseModelTaxonAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id, taxon):
        """
        Returns associations to models of the disease constrained by taxon

        See /disease/<id>/models route for full details

        """
        args = core_parser.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='model',
            subject=id,
            subject_direct=args.direct,
            invert_subject_object=True,
            object_taxon=taxon,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. Orphanet:399158, DOID:0080008. Equivalent IDs can be used with same results'})
class DiseaseGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a disease
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='genotype',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseasePublicationAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns publications associated with a disease
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='publication',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. DOID:4450. Equivalent IDs can be used with same results'})
class DiseasePathwayAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns pathways associated with a disease
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='pathway',
            subject=id,
            subject_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseVariantAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns variants associated with a disease
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='variant',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of disease, e.g. MONDO:0007103, MONDO:0010918. Equivalent IDs can be used with same results'})
class DiseaseCaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns cases associated with a disease
        """
        args = core_parser.parse_args()
        return search_associations(
            subject_category='disease',
            object_category='case',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier of phenotype, e.g. MP:0008521. Equivalent IDs can be used with same results'})
class PhenotypeAnatomyAssociations(Resource):
    # Note: This depends on https://github.com/biolink/biolink-api/issues/122
    @api.expect(core_parser)
    @api.marshal_list_with(named_object)
    def get(self, id):
        """
        Returns anatomical entities associated with a phenotype.

        Example IDs:

         * MP:0008521 abnormal Bowman membrane
        """
        clique_leader = scigraph.get_clique_leader(id)
        objs = scigraph.phenotype_to_entity_list(clique_leader.id)
        return objs

@api.doc(params={'id': 'CURIE identifier of phenotype, e.g. HP:0007359. Equivalent IDs can be used with same results'})
class PhenotypeDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(d2p_association_results)
    def get(self, id):
        """
        Returns diseases associated with a phenotype
        """
        args = core_parser_with_filters.parse_args()
        results = search_associations(
            subject_category='phenotype',
            object_category='disease',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            object_direct=args.direct,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )
        # fcs = results.get('facet_counts')
        # if fcs is not None:
        #     fcs['closure_bin'] = create_closure_bin(fcs.get('object_closure'))
        return results


@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  WBPhenotype:0000180 (axon morphology variant), MP:0001569 (abnormal circulating bilirubin level), '})
class PhenotypeGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a phenotype

        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='phenotype',
            object_category='gene',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )


@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  MP:0001569 (abnormal circulating bilirubin level)'})
@api.doc(params={'taxid': 'Species or high level taxon grouping, e.g  NCBITaxon:10090 (Mus musculus)'})
@api.deprecated
class PhenotypeGeneByTaxonAssociations(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id, taxid):
        """
        Returns gene IDs for all genes associated with a given phenotype, filtered by taxon

        For example, MP:0001569 + NCBITaxon:10090 (mouse)

        """
        args = core_parser.parse_args()
        return select_distinct_subjects(
            subject_category='gene',
            object_category='phenotype',
            object=id,
            object_direct=args.direct,
            subject_taxon=taxid,
            user_agent=USER_AGENT
        )

@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  WBPhenotype:0000180 (axon morphology variant), MP:0001569 (abnormal circulating bilirubin level)'})
class PhenotypeGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a phenotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='phenotype',
            object_category='genotype',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  WBPhenotype:0000180 (axon morphology variant), MP:0001569 (abnormal circulating bilirubin level)'})
class PhenotypePublicationAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns publications associated with a phenotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='phenotype',
            object_category='publication',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  MP:0001569 (abnormal circulating bilirubin level)'})
class PhenotypePathwayAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns pathways associated with a phenotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='phenotype',
            object_category='pathway',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  WBPhenotype:0000180 (axon morphology variant), MP:0001569 (abnormal circulating bilirubin level)'})
class PhenotypeVariantAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns variants associated with a phenotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='phenotype',
            object_category='variant',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  HP:0011951 (Aspiration pneumonia), HP:0002450 (Abnormal motor neuron morphology)'})
class PhenotypeCaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns cases associated with a phenotype
        """
        args = core_parser.parse_args()
        return search_associations(
            subject_category='phenotype',
            object_category='case',
            invert_subject_object=True,
            subject=id,
            subject_direct=args.direct,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.deprecated
@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0044598'})
class GotermGeneAssociations(Resource):

    parser = core_parser.copy()
    parser.add_argument(
        'relationship_type',
        choices=[INVOLVED_IN, INVOLVED_IN_REGULATION_OF, ACTS_UPSTREAM_OF_OR_WITHIN],
        default=INVOLVED_IN,
        help="relationship type ('{}', '{}' or '{}')".format(INVOLVED_IN, INVOLVED_IN_REGULATION_OF, ACTS_UPSTREAM_OF_OR_WITHIN)
    )

    @api.expect(parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns associations to GO terms for a gene
        """
        args = self.parser.parse_args()
        if args['relationship_type'] == ACTS_UPSTREAM_OF_OR_WITHIN:
            return search_associations(
                subject_category='gene',
                object_category='function',
                fq = {'regulates_closure': id},
                invert_subject_object=True,
                user_agent=USER_AGENT,
                **args)
        elif args['relationship_type'] == INVOLVED_IN_REGULATION_OF:
            # Temporary fix until https://github.com/geneontology/amigo/pull/469
            # and https://github.com/owlcollab/owltools/issues/241 are resolved
            return search_associations(
                subject_category = 'gene',
                object_category = 'function',
                fq = {'regulates_closure': id, '-isa_partof_closure': id},
                invert_subject_object=True,
                user_agent=USER_AGENT,
                **args)
        elif args['relationship_type'] == INVOLVED_IN:
            return search_associations(
                subject_category='gene',
                object_category='function',
                subject=id,
                invert_subject_object=True,
                user_agent=USER_AGENT,
                **args)


@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0044598'})
class FunctionGeneAssociations(Resource):

    parser = core_parser_with_filters.copy()
    parser.add_argument(
        'relationship_type',
        choices=[INVOLVED_IN, INVOLVED_IN_REGULATION_OF, ACTS_UPSTREAM_OF_OR_WITHIN],
        default=INVOLVED_IN,
        help="relationship type ('{}', '{}' or '{}')".format(INVOLVED_IN, INVOLVED_IN_REGULATION_OF, ACTS_UPSTREAM_OF_OR_WITHIN)
    )

    @api.expect(parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated to a GO term
        """
        args = self.parser.parse_args()
        if args['relationship_type'] == ACTS_UPSTREAM_OF_OR_WITHIN:
            return search_associations(
                subject_category='gene',
                object_category='function',
                fq={
                    'regulates_closure': id,
                },
                subject_taxon=args.taxon,
                invert_subject_object=True,
                user_agent=USER_AGENT,
                **args
            )
        elif args['relationship_type'] == INVOLVED_IN_REGULATION_OF:
            # Temporary fix until https://github.com/geneontology/amigo/pull/469
            # and https://github.com/owlcollab/owltools/issues/241 are resolved
            return search_associations(
                subject_category='gene',
                object_category='function',
                fq={
                    'regulates_closure': id,
                    '-isa_partof_closure': id,
                },
                subject_taxon=args.taxon,
                invert_subject_object=True,
                user_agent=USER_AGENT,
                **args
            )
        elif args['relationship_type'] == INVOLVED_IN:
            return search_associations(
                subject_category='gene',
                object_category='function',
                subject=id,
                subject_taxon=args.taxon,
                invert_subject_object=True,
                user_agent=USER_AGENT,
                **args
            )


@api.doc(params={'id': 'CURIE identifier of a function term (e.g. GO:0044598)'})
class FunctionAssociations(Resource):

    @api.expect(basic_parser)
    def get(self, id):
        """
        Returns annotations associated to a function term
        """

        # annotation_class,aspect
        fields = "date,assigned_by,bioentity_label,bioentity_name,synonym,taxon,taxon_label,panther_family,panther_family_label,evidence,evidence_type,reference,annotation_extension_class,annotation_extension_class_label"
        query_filters = "annotation_class%5E2&qf=annotation_class_label_searchable%5E1&qf=bioentity%5E2&qf=bioentity_label_searchable%5E1&qf=bioentity_name_searchable%5E1&qf=annotation_extension_class%5E2&qf=annotation_extension_class_label_searchable%5E1&qf=reference_searchable%5E1&qf=panther_family_searchable%5E1&qf=panther_family_label_searchable%5E1&qf=bioentity_isoform%5E1"
        args = basic_parser.parse_args()

        evidences = args['evidence']
        evidence = ""
        if evidences is not None:
            evidence = "&fq=evidence_closure:("
            for ev in evidences:
                evidence += "\"" + ev + "\","
            evidence = evidence[:-1]
            evidence += ")"

        taxon_restrictions = ""
        cfg = get_config()
        if cfg.taxon_restriction is not None:
            taxon_restrictions = "&fq=taxon_subset_closure:("
            for c in cfg.taxon_restriction:
                taxon_restrictions += "\"" + c + "\","
            taxon_restrictions = taxon_restrictions[:-1]
            taxon_restrictions += ")"


        optionals = "&defType=edismax&start=" + str(args['start']) + "&rows=" + str(args['rows']) + evidence + taxon_restrictions
        data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.ANNOTATION, id, query_filters, fields, optionals)
        
        return data


@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0044598'})
class FunctionTaxonAssociations(Resource):

    @api.expect(basic_parser)
    def get(self, id):
        """
        Returns taxons associated to a GO term
        """

        fields = "taxon,taxon_label"
        query_filters = "annotation_class%5E2&qf=annotation_class_label_searchable%5E1&qf=bioentity%5E2&qf=bioentity_label_searchable%5E1&qf=bioentity_name_searchable%5E1&qf=annotation_extension_class%5E2&qf=annotation_extension_class_label_searchable%5E1&qf=reference_searchable%5E1&qf=panther_family_searchable%5E1&qf=panther_family_label_searchable%5E1&qf=bioentity_isoform%5E1"
        args = basic_parser.parse_args()

        evidences = args['evidence']
        evidence = ""
        if evidences is not None:
            evidence = "&fq=evidence_closure:("
            for ev in evidences:
                evidence += "\"" + ev + "\","
            evidence = evidence[:-1]
            evidence += ")"

        taxon_restrictions = ""
        cfg = get_config()
        if cfg.taxon_restriction is not None:
            taxon_restrictions = "&fq=taxon_subset_closure:("
            for c in cfg.taxon_restriction:
                taxon_restrictions += "\"" + c + "\","
            taxon_restrictions = taxon_restrictions[:-1]
            taxon_restrictions += ")"
        

        optionals = "&defType=edismax&start=" + str(args['start']) + "&rows=" + str(args['rows']) + evidence + taxon_restrictions
        data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.ANNOTATION, id, query_filters, fields, optionals)
        
        return data


@api.doc(params={'id': 'CURIE identifier of a GO term, e.g. GO:0044598'})
class FunctionPublicationAssociations(Resource):

    @api.expect(basic_parser)
    def get(self, id):
        """
        Returns publications associated to a GO term
        """

        fields = "reference"
        query_filters = "annotation_class%5E2&qf=annotation_class_label_searchable%5E1&qf=bioentity%5E2&qf=bioentity_label_searchable%5E1&qf=bioentity_name_searchable%5E1&qf=annotation_extension_class%5E2&qf=annotation_extension_class_label_searchable%5E1&qf=reference_searchable%5E1&qf=panther_family_searchable%5E1&qf=panther_family_label_searchable%5E1&qf=bioentity_isoform%5E1"
        args = basic_parser.parse_args()

        evidences = args['evidence']
        evidence = ""
        if evidences is not None:
            evidence = "&fq=evidence_closure:("
            for ev in evidences:
                evidence += "\"" + ev + "\","
            evidence = evidence[:-1]
            evidence += ")"

        taxon_restrictions = ""
        cfg = get_config()
        if cfg.taxon_restriction is not None:
            taxon_restrictions = "&fq=taxon_subset_closure:("
            for c in cfg.taxon_restriction:
                taxon_restrictions += "\"" + c + "\","
            taxon_restrictions = taxon_restrictions[:-1]
            taxon_restrictions += ")"


        optionals = "&defType=edismax&start=" + str(args['start']) + "&rows=" + str(args['rows']) + evidence + taxon_restrictions
        data = run_solr_text_on(ESOLR.GOLR, ESOLRDoc.ANNOTATION, id, query_filters, fields, optionals)
        
        list = []
        for elt in data:
            for ref in elt['reference']:
                list.append(ref)

        return { "references": list }



@api.doc(params={'id': 'CURIE any pathway element. E.g. REACT:R-HSA-5387390'})
class PathwayGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a pathway
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='pathway',
            object_category='gene',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE any pathway element. E.g. REACT:R-HSA-5387390'})
class PathwayDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a pathway
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='pathway',
            object_category='disease',
            subject=id,
            subject_direct=args.direct,
            object_direct=args.direct,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE any pathway element. E.g. REACT:R-HSA-5387390'})
class PathwayPhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a pathway
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='pathway',
            object_category='phenotype',
            subject=id,
            subject_direct=args.direct,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of anatomical entity, e.g. GO:0005634 (nucleus), UBERON:0002037 (cerebellum), CL:0000540 (neuron). Equivalent IDs can be used with same results'})
class AnatomyGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a given anatomy
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='anatomical entity',
            object_category='gene',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of anatomical entity, e.g. GO:0005634 (nucleus), UBERON:0002037 (cerebellum), CL:0000540 (neuron). Equivalent IDs can be used with same results'})
@api.doc(params={'taxid': 'Species or high level taxon grouping, e.g  NCBITaxon:10090 (Mus musculus)'})
@api.deprecated
class AnatomyGeneByTaxonAssociations(Resource):

    @api.expect(core_parser_with_filters)
    #@api.marshal_list_with(association)
    def get(self, id, taxid):
        """
        Returns gene IDs for all genes associated with a given anatomy, filtered by taxon

        For example, + NCBITaxon:10090 (mouse)

        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='anatomical entity',
            object_category='gene',
            subject=id,
            object_taxon=taxid,
            object_taxon_direct=args.direct_taxon,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of substance, e.g. CHEBI:40036'})
class SubstanceRoleAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns associations between given drug and roles

        Roles may be human-oriented (e.g. pesticide) or molecular (e.g. enzyme inhibitor)
        """
        return scigraph.substance_to_role_associations(id)

@api.doc(params={'id': 'CURIE identifier of substance, e.g. CHEBI:40036'})
class SubstanceParticipantInAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns associations between an activity and process and the specified substance

        Examples relationships:

         * substance is a metabolite of a process
         * substance is synthesized by a process
         * substance is modified by an activity
         * substance elicits a response program/pathway
         * substance is transported by activity or pathway

        For example, CHEBI:40036 (amitrole)

        """
        return scigraph.substance_participates_in_associations(id)


@api.doc(params={'id': 'CURIE identifier of substance, e.g. CHEBI:40036'})
class SubstanceTreatsAssociations(Resource):

    @api.expect(core_parser)
    #TODO: @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns substances associated with a disease.

        e.g. drugs or small molecules used to treat

        """
        return condition_to_drug(id)

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes-genotype associations.

        Genotypes may be related to one another according to the GENO model
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='genotype',
            object_category='genotype',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. MONARCH:FBgeno422705'})
class GenotypeVariantAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes-variant associations.
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='genotype',
            object_category='variant',
            invert_subject_object=True,
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-4286'})
class GenotypePhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a genotype
        """
        args = core_parser_with_filters.parse_args()
        results = search_associations(
            subject_category='genotype',
            object_category='phenotype',
            subject=id,
            object_direct=args.direct,
            facet_limit=100000,
            user_agent=USER_AGENT,
            **args
        )

        fcs = results.get('facet_counts')
        if fcs:
            closure_bin, slim_facet = create_closure_bin(fcs.get('object_closure'))
            fcs['closure_bin'] = closure_bin
            fcs['object_closure'] = slim_facet

        return results

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. dbSNPIndividual:11441 (if non-human will return models)'})
class GenotypeDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a genotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='genotype',
            object_category='disease',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a genotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='genotype',
            object_category='gene',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeModelAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns models associated with a genotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='genotype',
            object_category='model',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypePublicationAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns publications associated with a genotype
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='genotype',
            object_category='publication',
            subject=id,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of genotype, e.g. dbSNPIndividual:10440, dbSNPIndividual:22633'})
class GenotypeCaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns cases associated with a genotype
        """

        return search_associations(
            subject_category='genotype',
            object_category='case',
            subject=id,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8'})
class VariantGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a variant
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='variant',
            object_category='genotype',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of variant, e.g. ClinVarVariant:14925'})
class VariantDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a variant
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='variant',
            object_category='disease',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantPhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a variant
        """
        args = core_parser_with_filters.parse_args()
        results = search_associations(
            subject_category='variant',
            object_category='phenotype',
            subject=id,
            object_direct=args.direct,
            facet_limit=100000,
            user_agent=USER_AGENT,
            **args
        )

        fcs = results.get('facet_counts')
        if fcs:
            closure_bin, slim_facet = create_closure_bin(fcs.get('object_closure'))
            fcs['closure_bin'] = closure_bin
            fcs['object_closure'] = slim_facet

        return results

@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a variant
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='variant',
            object_category='gene',
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantPublicationAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns publications associated with a variant
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='variant',
            object_category='publication',
            subject=id,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier of variant, e.g. OMIM:607623.0012, dbSNP:rs5030868'})
class VariantModelAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns models associated with a variant
        """

        return search_associations(
            subject_category='variant',
            object_category='model',
            subject=id,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier of variant, e.g. OMIM:309550.0004, dbSNP:rs5030868'})
class VariantCaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns cases associated with a variant
        """

        return search_associations(
            subject_category='variant',
            object_category='case',
            subject=id,
            invert_subject_object=True,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier for a model, e.g. MGI:5573196'})
class ModelDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a model
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='model',
            object_category='disease',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a model, e.g. MMRRC:042787'})
class ModelGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a model
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='model',
            object_category='gene',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a model, e.g. Coriell:NA16660'})
class ModelGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a model
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='model',
            object_category='genotype',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a model, e.g. MGI:5644542'})
class ModelPublicationAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns publications associated with a model
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='model',
            object_category='publication',
            invert_subject_object=True,
            subject=id,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'id'})
class ModelPhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a model
        """
        args = core_parser_with_filters.parse_args()
        results = search_associations(
            subject_category='model',
            object_category='phenotype',
            subject=id,
            object_direct=args.direct,
            facet_limit=100000,
            user_agent=USER_AGENT,
            **args
        )

        fcs = results.get('facet_counts')
        if fcs:
            closure_bin, slim_facet = create_closure_bin(fcs.get('object_closure'))
            fcs['closure_bin'] = closure_bin
            fcs['object_closure'] = slim_facet

        return results

@api.doc(params={'id': 'CURIE identifier for a model, e.g. MMRRC:042787'})
class ModelVariantAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns variants associated with a model
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='model',
            object_category='variant',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a model, e.g. Coriell:GM22295, Coriell:HG02187'})
class ModelCaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns cases associated with a model
        """

        return search_associations(
            subject_category='model',
            object_category='case',
            subject=id,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier for a publication, e.g. PMID:11751940'})
class PublicationVariantAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns variants associated with a publication
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='publication',
            object_category='variant',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a publication, e.g. PMID:11751940'})
class PublicationPhenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a publication
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='publication',
            object_category='phenotype',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a publication, e.g. PMID:11751940'})
class PublicationModelAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns models associated with a publication
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='publication',
            object_category='model',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a publication, e.g. PMID:11751940'})
class PublicationGenotypeAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a publication
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='publication',
            object_category='genotype',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a publication, e.g. PMID:11751940'})
class PublicationGeneAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a publication
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='publication',
            object_category='gene',
            subject=id,
            object_taxon=args.taxon,
            object_taxon_direct=args.direct_taxon,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a publication, e.g. PMID:11751940'})
class PublicationDiseaseAssociations(Resource):

    @api.expect(core_parser_with_filters)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a publication
        """
        args = core_parser_with_filters.parse_args()
        return search_associations(
            subject_category='publication',
            object_category='disease',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **args
        )

@api.doc(params={'id': 'CURIE identifier for a case'})
class CaseModelAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns models associated with a case
        """

        return search_associations(
            subject_category='case',
            object_category='model',
            invert_subject_object=True,
            subject=id,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier for a case'})
class CaseDiseaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a case
        """
        args = core_parser.parse_args()
        return search_associations(
            subject_category='case',
            object_category='disease',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier for a case'})
class CaseVariantAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns variants associated with a case
        """

        return search_associations(
            subject_category='case',
            object_category='variant',
            subject=id,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier for a case'})
class CaseGenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a case
        """

        return search_associations(
            subject_category='case',
            object_category='genotype',
            subject=id,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )

@api.doc(params={'id': 'CURIE identifier for a case'})
class CasePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a case
        """
        args = core_parser.parse_args()
        return search_associations(
            subject_category='case',
            object_category='phenotype',
            subject=id,
            object_direct=args.direct,
            user_agent=USER_AGENT,
            **core_parser.parse_args()
        )
