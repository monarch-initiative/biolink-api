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

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bioentity', description='Retrieval of domain entities plus associations')

core_parser = api.parser()
core_parser.add_argument('rows', type=int, required=False, default=20, help='number of rows')
core_parser.add_argument('unselect_evidence', type=bool, help='If set, excludes evidence objects in response')
core_parser.add_argument('exclude_automatic_assertions', default=False, type=bool, help='If set, excludes associations that involve IEAs (ECO:0000501)')
core_parser.add_argument('fetch_objects', type=bool, default=True, help='If true, returns a distinct set of association.objects (typically ontology terms). This appears at the top level of the results payload')
core_parser.add_argument('use_compact_associations', type=bool, default=False, help='If true, returns results in compact associations format')
core_parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID or subset ID')
core_parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)

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
    @api.marshal_list_with(bio_object)
    def get(self, id):
        """
        TODO Returns object of any type
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
    @api.marshal_list_with(gene)
    def get(self, id):
        """
        Returns gene object
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
        homolog_args = homolog_parser.parse_args()
        return search_associations(
            subject_category='gene', object_category='gene',
            relation=homol_rel, subject=id,
            object_taxon=homolog_args.homolog_taxon,
            **homolog_parser.parse_args())
    
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
        print(args)

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

@ns.route('/gene/<id>/expressed/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GeneExpressionAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        TODO Returns expression events for a gene
        """

        return search_associations(
            subject_category='gene', object_category='anatomy',
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
            logging.debug("Found no associations using {} - will try mapping to other IDs".format(id))
            sg_dev = SciGraph(url='https://scigraph-data-dev.monarchinitiative.org/scigraph/')
            prots = sg_dev.gene_to_uniprot_proteins(id)
            for prot in prots:
                pr_assocs = search_associations(
                        object_category='function',
                        subject=prot, **core_parser.parse_args())
                assocs['associations'] += pr_assocs['associations']
        return assocs
    
@ns.route('/gene/<id>/pubs/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GenePublicationList(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        TODO Returns expression events for a gene
        """

        # TODO: we don't store this directly
        # could be retrieved by getting all associations and then extracting pubs
        return search_associations(
            subject_category='gene', object_category='publication',
            subject=id, **core_parser.parse_args())
    
@ns.route('/geneproduct/<id>')
class GeneproductObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns gene product object
        """
        return { 'foo' : 'bar' }
    
@ns.route('/disease/<id>')
class DiseaseObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns disease object
        """
        return { 'foo' : 'bar' }

@ns.route('/disease/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseasePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with disease
        """

        return search_associations(
            subject_category='disease', object_category='phenotype',
            subject=id, **core_parser.parse_args())

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

@ns.route('/disease/<id>/anatomy/')
class DiseaseAnatomyAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns anatomical locations associated with a disease.

        For example, neurodegeneratibe disease located in nervous system.
        For cancer, this may include both site of original and end location.
        """
        return { 'foo' : 'bar' }
    
@ns.route('/disease/<id>/function/')
class DiseaseFunctionAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns biological functions associated with a disease.

        This may come from a combination of asserted knowledge (e.g. Fanconi Anemia affects DNA repair)
        or from data-driven approach (cf Translator)

        Results are typically represented as GO classes
        """
        return { 'foo' : 'bar' }

@ns.route('/disease/<id>/substance/')
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
        Same as `/disease/<id>/models` but constrain models by taxon

        """
        # TODO: invert
        return search_associations(
            subject_category='disease', object_category='model',
            subject=id, invert_subject_object=True,
            object_taxon=taxon, **core_parser.parse_args())

@ns.route('/phenotype/<id>')
class PhenotypeObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns phenotype class object
        """
        return { 'foo' : 'bar' }
    
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
        TODO Returns biological functions associated with a Phenotype.

        This may come from a combination of asserted knowledge (e.g. abnormal levels of metabolite to corresponding GO activity)
        or from data-driven approach (cf Translator)

        Results are typically represented as GO classes
        """
        return { 'foo' : 'bar' }
    
@ns.route('/phenotype/<id>/phenotype/')
class PhenotypePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associated phenotypes

        Includes phenologs, as well as equivalent phenotypes in other species
        """
        return { 'foo' : 'bar' }

@ns.route('/phenotype/<id>/genes/')
class PhenotypeGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associated phenotypes

        """
        return { 'foo' : 'bar' }

@ns.route('/phenotype/<id>/gene/<taxid>/ids')
@api.doc(params={'id': 'Pheno class CURIE identifier, e.g  MP:0001569 (abnormal circulating bilirubin level)'})
@api.doc(params={'taxid': 'Species or high level taxon grouping, e.g  NCBITaxon:10090 (Mus musculus)'})
class PhenotypeGeneAssociations(Resource):

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
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns GO class object
        """
        return { 'foo' : 'bar' }

@ns.route('/goterm/<id>/phenotype/')
class GotermPhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associated phenotypes

        """
        return { 'foo' : 'bar' }

@ns.route('/goterm/<id>/genes/')
class GotermGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_with(association_results)
    def get(self, id):
        """
        TODO Returns associated genes

        """
        return search_associations(
            subject_category='gene', object_category='function',
            subject=id, invert_subject_object=True, **core_parser.parse_args())
    
@ns.route('/pathway/<id>')
@api.doc(params={'id': 'CURIE any pathway element. May be a GO ID or a pathway database ID'})
class PathwayObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns pathway object
        """
        return { 'foo' : 'bar' }
    
@ns.route('/pathway/<id>/genes/')
class PathwayGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns list of genes associated with a pathway
        """
        return { 'foo' : 'bar' }

@ns.route('/pathway/<id>/participants/')
class PathwayParticipantAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations to participants (molecules, etc) for a pathway
        """
        return { 'foo' : 'bar' }

@ns.route('/literature/<id>')
class PubObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(publication)
    def get(self, id):
        """
        TODO Returns publication object
        """
        return { 'id' : 'PMID:1' }

@ns.route('/literature/<id>/genes/')
class LiteratureGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns associations between a lit entity and a gene
        """
        return search_associations(
            subject_category='literature', object_category='gene',
            subject=id, **core_parser.parse_args())

@ns.route('/literature/<id>/diseases/')
class LiteratureDiseaseAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns associations between a lit entity and a disease
        """
        return search_associations(
            subject_category='literature', object_category='disease',
            subject=id, **core_parser.parse_args())

@ns.route('/literature/<id>/genotypes/')
class LiteratureGenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns associations between a lit entity and a genotype
        """
        return search_associations(
            subject_category='literature', object_category='genotype',
            subject=id, **core_parser.parse_args())

@ns.route('/anatomy/<id>')
@api.doc(params={'id': 'CURIE identifier of anatomical entity, e.g. GO:0005634 (nucleus), UBERON:0002037 (cerebellum), CL:0000540 (neuron). Equivalent IDs can be used with same results'})
class AnatomyObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns anatomical entity

        Anatomical entities span ranges from the subcellular (e.g. nucleus) through cells to tissues, organs and organ systems.

        When returning associations, inference over the appropriate relation will be used. For example, for gene expression, part-of will be used.
        """
        obj = scigraph.bioobject(id)
        return obj

@ns.route('/anatomy/<id>/genes/')
class AnatomyGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between anatomical entity and genes

        Typically encompasses genes expressed in a particular location.

        INFERENCE: part-of
        """
        return { 'foo' : 'bar' }

@ns.route('/anatomy/<id>/phenotypes/')
class AnatomyPhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between anatomical entity and phenotypes
        """
        return { 'foo' : 'bar' }
    

@ns.route('/environment/<id>')
class EnvironmentObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns environment entity

        TODO consider renaming exposure
        """
        return { 'foo' : 'bar' }
    
@ns.route('/environment/<id>/phenotypes/')
class EnvironmentPhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns list of associations
        """
        return { 'foo' : 'bar' }

@ns.route('/substance/<id>')
class SubstanceObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(substance)
    def get(self, id):
        """
        TODO Returns substance entity
        """
        return { 'foo' : 'bar' }

@ns.route('/substance/<id>/targets/')
class SubstanceTargetAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between given drug and targets
        """
        return { 'foo' : 'bar' }

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

@ns.route('/substance/<id>/interactions/')
class SubstanceInteractions(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between given drug and interactions

        Interactions can encompass drugs or environments
        """
        return { 'foo' : 'bar' }
    
@ns.route('/substance/<id>/substances/')
class SubstanceRelationships(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between a substance and other substances

        E.g. metabolite-of, tautomer-of, parent-of, ...
        """
        return { 'foo' : 'bar' }
    
@ns.route('/substance/<id>/exposures/')
class SubstanceExposures(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between a substance and related exposures

        E.g. between pesticide and occupational exposure class
        """
        return { 'foo' : 'bar' }
    
@ns.route('/substance/<id>/treats/')
class DiseaseSubstanceAssociations(Resource):

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

        # TODO: invert
        return search_associations(
            subject_category='genotype', object_category='phenotypes',
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
    @api.marshal_list_with(allele)
    def get(self, id):
        """
        TODO Returns allele object

        This is a composition of multiple smaller operations,
        including fetching allele metadata, plus allele associations

        TODO - should allele be subsumed into variant?
        """
        return { 'id' : 'foobar' }
    

@ns.route('/variant/<id>')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns sequence variant entity
        """
        return { 'foo' : 'bar' }

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
            subject_category='variant', object_category='phenotypes',
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
    
@ns.route('/sequence_feature/<id>')
class SequenceFeatureObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns seqfeature
        """
        return { 'foo' : 'bar' }


@ns.route('/individual/<id>')
class ParentObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns individual

        Individuals may typically encompass patients, but can be individuals of any species
        """
        return { 'foo' : 'bar' }

@ns.route('/investigation/<id>')
class ParentObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns investigation object

        Investigations encompass clinical trials, molecular biology experiments or any kind of study
        """
        return { 'foo' : 'bar' }
    
    

