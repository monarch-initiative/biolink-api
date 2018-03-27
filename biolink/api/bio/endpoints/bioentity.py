import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import node, named_object, bio_object, association_results, association, publication, gene, substance, genotype, allele, search_result
#import biolink.datamodel.serializers
from biolink.api.restplus import api
from ontobio.golr.golr_associations import search_associations, search_associations_go, select_distinct_subjects
from scigraph.scigraph_util import SciGraph
from biowikidata.wd_sparql import doid_to_wikidata, resolve_to_wikidata, condition_to_drug
from ontobio.vocabulary.relations import HomologyTypes
from ..closure_bins import create_closure_bin

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bioentity', description='Retrieval of domain entities plus associations')

core_parser = api.parser()
core_parser.add_argument('rows', type=int, required=False, default=100, help='number of rows')
core_parser.add_argument('start', type=int, required=False, help='beginning row')
core_parser.add_argument('unselect_evidence', type=bool, help='If set, excludes evidence objects in response')
core_parser.add_argument('exclude_automatic_assertions', default=False, type=bool, help='If set, excludes associations that involve IEAs (ECO:0000501)')
core_parser.add_argument('fetch_objects', type=bool, default=True, help='If true, returns a distinct set of association.objects (typically ontology terms). This appears at the top level of the results payload')
core_parser.add_argument('use_compact_associations', type=bool, default=False, help='If true, returns results in compact associations format')
core_parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID or subset ID')
core_parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)

INVOLVED_IN = 'involved_in'
INVOLVED_IN_REGULATION_OF = 'involved_in_regulation_of'
ACTS_UPSTREAM_OF_OR_WITHIN = 'acts_upstream_of_or_within'

core_parser_with_rel = core_parser.copy()
core_parser_with_rel.add_argument('relationship_type', choices=[INVOLVED_IN, INVOLVED_IN_REGULATION_OF, ACTS_UPSTREAM_OF_OR_WITHIN], help="relationship type ('{}', '{}' or '{}')".format(INVOLVED_IN, INVOLVED_IN_REGULATION_OF, ACTS_UPSTREAM_OF_OR_WITHIN))


scigraph = SciGraph('https://scigraph-data.monarchinitiative.org/scigraph/')

homol_rel = HomologyTypes.Homolog.value

def get_object_gene(id, **args):
        obj = scigraph.bioobject(id, 'Gene')
        obj.phenotype_associations = search_associations(subject=id, object_category='phenotype', **args)['associations']
        obj.homology_associations = search_associations(subject=id, rel=homol_rel, object_category='gene', **args)['associations']
        obj.disease_associations = search_associations(subject=id, object_category='disease', **args)['associations']
        obj.genotype_associations = search_associations(subject=id, invert_subject_object=True, object_category='genotype', **args)['associations']

        return(obj)

def get_object_genotype(id, **args):
        obj = scigraph.bioobject(id, 'Genotype')
        obj.phenotype_associations = search_associations(subject=id, object_category='phenotype', **args)['associations']
        obj.disease_associations = search_associations(subject=id, object_category='disease', **args)['associations']
        obj.gene_associations = search_associations(subject=id, object_category='gene', **args)['associations']

        return(obj)

@ns.route('/<id>')
@api.doc(params={'id': 'id, e.g. NCBIGene:84570'})
class GenericObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on object of any type
        """
        obj = scigraph.bioobject(id)
        return(obj)

@ns.route('/<id>/associations/')
class GenericAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns associations for an entity regardless of the type
        """
        return search_associations(subject=id, **core_parser.parse_args())

@ns.route('/gene/<id>')
@api.doc(params={'id': 'id, e.g. NCBIGene:84570'})
class GeneObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(gene)
    def get(self, id):
        """
        Returns basic info about a gene
        """
        return get_object_gene(id)

@api.doc(params={'id': 'id, e.g. NCBIGene:3630. Equivalent IDs can be used with same results'})
class AbstractGeneAssociationResource(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        pass

@ns.route('/gene/<id>/interactions/')
class GeneInteractions(AbstractGeneAssociationResource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns interactions for a gene
        """
        return search_associations(
            subject_category='gene', object_category='gene',
            relation='RO:0002434', subject=id, **core_parser.parse_args())

homolog_parser = core_parser.copy()
homolog_parser.add_argument('homolog_taxon', help='Taxon CURIE of homolog, e.g. NCBITaxon:9606. Can be intermediate note, includes inferred by default')
homolog_parser.add_argument('homology_type', choices=['P', 'O', 'LDO'], help='P, O or LDO (paralog, ortholog or least-diverged).')

@ns.route('/gene/<id>/homologs/')
class GeneHomologAssociations(AbstractGeneAssociationResource):

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
        results = search_associations(
            subject_category='gene', object_category='gene',
            relation=homol_rel, subject=id,
            object_taxon=homolog_args.homolog_taxon,
            **homolog_parser.parse_args())
        return results

@ns.route('/gene/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GenePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with gene
        """
        args = core_parser.parse_args()

        return search_associations(
            subject_category='gene', object_category='phenotype',
            subject=id, **core_parser.parse_args())

@ns.route('/gene/<id>/diseases/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750, Orphanet:173505. Equivalent IDs can be used with same results'})
class GeneDiseaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with gene
        """
        args = core_parser.parse_args()
        print(args)

        return search_associations(
            subject_category='gene', object_category='disease',
            subject=id, **core_parser.parse_args())

@ns.route('/gene/<id>/pathways/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:50846. Equivalent IDs can be used with same results'})
class GenePathwayAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns pathways associated with gene
        """
        args = core_parser.parse_args()

        return search_associations(
            subject_category='gene', object_category='pathway',
            subject=id, **core_parser.parse_args())

@ns.route('/gene/<id>/expression/anatomy')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GeneExpressionAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns expression events for a gene
        """

        return search_associations(
            subject_category='gene', object_category='anatomical entity',
            subject=id, **core_parser.parse_args())

@ns.route('/gene/<id>/function/')
class GeneFunctionAssociations(AbstractGeneAssociationResource):

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
            subject=id, **core_parser.parse_args())

        # If there are no associations for the given ID, try other IDs.
        # Note the AmiGO instance does *not* support equivalent IDs
        if len(assocs['associations']) == 0:
            # Note that GO currently uses UniProt as primary ID for some sources: https://github.com/biolink/biolink-api/issues/66
            # https://github.com/monarch-initiative/dipper/issues/461
            #sg_dev = SciGraph(url='https://scigraph-data.monarchinitiative.org/scigraph/')
            sg_dev = scigraph
            prots = sg_dev.gene_to_uniprot_proteins(id)
            for prot in prots:
                pr_assocs = search_associations(
                        object_category='function',
                        subject=prot, **core_parser.parse_args())
                assocs['associations'] += pr_assocs['associations']
        return assocs


@ns.route('/disease/<id>')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, Orphanet:1934, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on a disease
        """
        obj = scigraph.bioobject(id)
        return(obj)

@ns.route('/disease/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, Orphanet:1934, DOID:678. Equivalent IDs can be used with same results'})
class DiseasePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with disease
        """

        results = search_associations(
                subject_category='disease', object_category='phenotype',
                subject=id, **core_parser.parse_args())
        fcs = results.get('facet_counts')
        if fcs is not None:
            fcs['closure_bin'] = create_closure_bin(fcs.get('object_closure'))
        return results

@ns.route('/disease/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a disease
        """
        args = core_parser.parse_args()
        return search_associations(
            subject_category='disease', object_category='gene',
            subject=id, invert_subject_object=True, **core_parser.parse_args())


@ns.route('/disease/<id>/treatment/')
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

@ns.route('/disease/<id>/models/')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseModelAssociations(Resource):

    @api.expect(core_parser)
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

        return search_associations(
            subject_category='disease', object_category='model',
            subject=id, invert_subject_object=True, **core_parser.parse_args())

@ns.route('/disease/<id>/models/<taxon>')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
@api.doc(params={'taxon': 'CURIE of organism taxonomy class to constrain models, e.g NCBITaxon:6239 (C elegans).\n\n Higher level taxa may be used'})
class DiseaseModelTaxonAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id, taxon):
        """
        Returns associations to models of the disease constrained by taxon

        See /disease/<id>/models route for full details

        """
        # TODO: invert
        return search_associations(
            subject_category='disease', object_category='model',
            subject=id, invert_subject_object=True,
            object_taxon=taxon, **core_parser.parse_args())

@ns.route('/phenotype/<id>')
@api.doc(params={'id': 'CURIE identifier of phenotype, e.g. MP:0008521, MP:0013166, WBPhenotype:0000180 '})
class PhenotypeObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on a phenotype
        """
        obj = scigraph.bioobject(id)
        return(obj)

@ns.route('/phenotype/<id>/anatomy/')
class PhenotypeAnatomyAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(named_object)
    def get(self, id):
        """
        Returns anatomical entities associated with a phenotype.

        Example IDs:

         * ZP:0004204
         * MP:0008521 abnormal Bowman membrane

        For example, *abnormal limb development* will map to *limb*
        """
        objs = scigraph.phenotype_to_entity_list(id)
        return objs


@ns.route('/phenotype/<id>/function/')
class PhenotypeFunctionAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns biological functions associated with a Phenotype.

        This may come from a combination of asserted knowledge (e.g. abnormal levels of metabolite to corresponding GO activity)
        or from data-driven approach (cf Translator)

        Results are typically represented as GO classes
        """
        return { 'foo' : 'bar' }


@ns.route('/phenotype/<id>/genes/')
@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  WBPhenotype:0000180 (axon morphology variant), MP:0001569 (abnormal circulating bilirubin level), '})
class PhenotypeGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns associated phenotypes

        """
        return search_associations(
            subject_category='gene', object_category='phenotype',
            object=id, **core_parser.parse_args())


@ns.route('/phenotype/<id>/gene/<taxid>/ids')
@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  MP:0001569 (abnormal circulating bilirubin level)'})
@api.doc(params={'taxid': 'Species or high level taxon grouping, e.g  NCBITaxon:10090 (Mus musculus)'})
class PhenotypeGeneByTaxonAssociations(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id, taxid):
        """
        Returns gene ids for all genes for a particular phenotype in a taxon

        For example, + NCBITaxon:10090 (mouse)

        """
        results = select_distinct_subjects(subject_category='gene',
                                           object_category='phenotype',
                                           subject_taxon=taxid)
        return results

@ns.route('/goterm/<id>')
@api.doc(params={'id': 'GO class CURIE identifier, e.g GO:0016301 (kinase activity)'})
class GotermObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on a gene
        """
        obj = scigraph.bioobject(id)
        return(obj)


@ns.route('/goterm/<id>/genes/')
class GotermGeneAssociations(Resource):

    @api.expect(core_parser_with_rel)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns associations to GO terms for a gene
        """
        args = core_parser_with_rel.parse_args()
        if args['relationship_type'] == ACTS_UPSTREAM_OF_OR_WITHIN:
            return search_associations(
                subject_category='gene', object_category='function',
                fq = {'regulates_closure': id},
                invert_subject_object=True, **args)
        elif args['relationship_type'] == INVOLVED_IN_REGULATION_OF:
            # Temporary fix until https://github.com/geneontology/amigo/pull/469
            # and https://github.com/owlcollab/owltools/issues/241 are resolved
            return search_associations(
                subject_category = 'gene', object_category = 'function',
                fq = {'regulates_closure': id, '-isa_partof_closure': id},
                invert_subject_object=True, **args)
        elif args['relationship_type'] == INVOLVED_IN:
            return search_associations(
                subject_category='gene', object_category='function',
                subject=id, invert_subject_object=True, **core_parser.parse_args())

@ns.route('/pathway/<id>')
@api.doc(params={'id': 'CURIE any pathway element. May be a GO ID or a pathway database ID'})
class PathwayObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on a pathway
        """
        obj = scigraph.bioobject(id)
        return(obj)

@ns.route('/pathway/<id>/genes/')
@api.doc(params={'id': 'CURIE any pathway element. E.g. REACT:R-HSA-5387390'})
class PathwayGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a pathway
        """
        args = core_parser.parse_args()

        return search_associations(
            subject_category='gene', object_category='pathway',
            object=id, **core_parser.parse_args())


@ns.route('/anatomy/<id>')
@api.doc(params={'id': 'CURIE identifier of anatomical entity, e.g. GO:0005634 (nucleus), UBERON:0002037 (cerebellum), CL:0000540 (neuron). Equivalent IDs can be used with same results'})
class AnatomyObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on anatomical entity

        Anatomical entities span ranges from the subcellular (e.g. nucleus) through cells to tissues, organs and organ systems.

        When returning associations, inference over the appropriate relation will be used. For example, for gene expression, part-of will be used.
        """
        obj = scigraph.bioobject(id)
        return obj

@ns.route('/anatomy/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of anatomical entity, e.g. GO:0005634 (nucleus), UBERON:0002037 (cerebellum), CL:0000540 (neuron). Equivalent IDs can be used with same results'})
class AnatomyGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns expression events for a gene
        """

        return search_associations(
            subject_category='gene', object_category='anatomical entity',
            object=id, **core_parser.parse_args())

@ns.route('/anatomy/<id>/genes/<taxid>')
@api.doc(params={'id': 'CURIE identifier of anatomical entity, e.g. GO:0005634 (nucleus), UBERON:0002037 (cerebellum), CL:0000540 (neuron). Equivalent IDs can be used with same results'})
@api.doc(params={'taxid': 'Species or high level taxon grouping, e.g  NCBITaxon:10090 (Mus musculus)'})
class AnatomyGeneByTaxonAssociations(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id, taxid):
        """
        Returns gene ids for all genes for a particular anatomy in a taxon

        For example, + NCBITaxon:10090 (mouse)

        """
        return search_associations(
                subject_category='gene',
                object_category='anatomical entity',
                subject_taxon=taxid,
                object=id, **core_parser.parse_args())

@ns.route('/substance/<id>')
class SubstanceObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on a substance

        This can be classes from CHEBI
        """
        obj = scigraph.bioobject(id)
        return obj


@ns.route('/substance/<id>/roles/')
class SubstanceRoleAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns associations between given drug and roles

        Roles may be human-oriented (e.g. pesticide) or molecular (e.g. enzyme inhibitor)
        """
        return scigraph.substance_to_role_associations(id)

@ns.route('/substance/<id>/participant_in/')
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


@ns.route('/substance/<id>/treats/')
class SubstanceTreatsAssociations(Resource):

    @api.expect(core_parser)
    #TODO: @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns substances associated with a disease.

        e.g. drugs or small molecules used to treat

        """
        return condition_to_drug(id)


@ns.route('/genotype/<id>')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(genotype)
    def get(self, id):
        """
        Returns genotype object.

        The genotype object will have the following association sets populated:

         * gene
         * phenotype
         * disease

        """
        return get_object_genotype(id)

@ns.route('/genotype/<id>/genotypes/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeGenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes-genotype associations.

        Genotypes may be related to one another according to the GENO model
        """

        # TODO: invert
        return search_associations(
            subject_category='genotype', object_category='genotype',
            subject=id, **core_parser.parse_args())

@ns.route('/genotype/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-4286'})
class GenotypePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a genotype
        """

        return search_associations(
            subject_category='genotype', object_category='phenotype',
            subject=id, **core_parser.parse_args())

@ns.route('/genotype/<id>/diseases/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-4286 (if non-human will return models)'})
class GenotypeDiseaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns diseases associated with a genotype
        """

        # TODO: invert
        return search_associations(
            subject_category='genotype', object_category='disease',
            subject=id, **core_parser.parse_args())

@ns.route('/genotype/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a genotype
        """

        # TODO: invert
        return search_associations(
            subject_category='genotype', object_category='gene',
            subject=id, **core_parser.parse_args())

##

@ns.route('/allele/<id>')
class AlleleObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(genotype)
    def get(self, id):
        """
        Returns genotype object.

        The genotype object will have the following association sets populated:

         * gene
         * phenotype
         * disease

        """
        return get_object_genotype(id)


@ns.route('/variant/<id>')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on a variant
        """
        obj = scigraph.bioobject(id)
        return obj

@ns.route('/variant/<id>/genotypes/')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantGenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a variant
        """

        # TODO: invert
        return search_associations(
            subject_category='variant', object_category='genotype',
            subject=id, **core_parser.parse_args())

@ns.route('/variant/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantPhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a variant
        """

        # TODO: invert
        return search_associations(
            subject_category='variant', object_category='phenotype',
            subject=id, **core_parser.parse_args())

@ns.route('/variant/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a variant
        """

        # TODO: invert
        return search_associations(
            subject_category='variant', object_category='gene',
            subject=id, **core_parser.parse_args())

#@ns.route('/sequence_feature/<id>')
#class SequenceFeatureObject(Resource):
#
#    @api.expect(core_parser)
#    #@api.marshal_list_with(association)
#    def get(self, id):
#        """
#        TODO Returns seqfeature
#        """
#        return { 'foo' : 'bar' }


@ns.route('/individual/<id>')
class ParentObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(bio_object)
    def get(self, id):
        """
        Returns basic info on an individual/case
        """
        obj = scigraph.bioobject(id)
        return obj
