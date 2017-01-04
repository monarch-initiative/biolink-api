import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import named_object, association_results, association, publication, gene, drug, genotype, allele, search_result
#import biolink.datamodel.serializers
from biolink.api.restplus import api
from biogolr.golr_associations import search_associations, search_associations_go
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bioentity', description='Retrieval of domain entities plus associations')

core_parser = api.parser()
core_parser.add_argument('rows', type=int, required=False, default=20, help='number of rows')
core_parser.add_argument('unselect_evidence', type=bool, help='If set, excludes evidence objects in response')
core_parser.add_argument('exclude_automatic_assertions', default=False, type=bool, help='If set, excludes associations that involve IEAs (ECO:0000501)')
core_parser.add_argument('fetch_objects', type=bool, default=True, help='If true, returns a distinct set of association.objects (typically ontology terms). This appears at the top level of the results payload')

@ns.route('/<id>')
@api.doc(params={'id': 'id, e.g. NCBIGene:84570'})
class GenericObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(named_object)
    def get(self, id):
        """
        TODO Returns object of any type
        """
        return { 'foo' : 'bar' }

@ns.route('/<id>/associations/')
class GenericAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns associations for an entity regardless of the type
        """
        return search_associations(None, None, None, id, **core_parser.parse_args())
    
@ns.route('/gene/<id>')
@api.doc(params={'id': 'id, e.g. NCBIGene:84570'})
class GeneObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(gene)
    def get(self, id):
        """
        TODO Returns gene object
        """
        return { 'foo' : 'bar' }

@api.doc(params={'id': 'id, e.g. NCBIGene:3630. Equivalent IDs can be used with same results'})
class AbstractGeneAssociationResource(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        pass
    
@ns.route('/gene/<id>/interactions/')
class GeneInteractions(AbstractGeneAssociationResource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns interactions for a gene
        """
        return search_associations('gene', 'gene', 'RO:0002434', id, **core_parser.parse_args())

homolog_parser = api.parser()
homolog_parser.add_argument('homolog_taxon', help='Taxon CURIE of homolog, e.g. NCBITaxon:9606. Can be intermediate note, includes inferred by default')
homolog_parser.add_argument('type', choices=['P', 'O', 'LDO'], help='P, O or LDO (paralog, ortholog or least-diverged).')

@ns.route('/gene/<id>/homologs/')
class GeneHomologAssociations(AbstractGeneAssociationResource):

    @api.expect(homolog_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns homologs for a gene
        """
        rel = 'RO:0002434'  # TODO
        return search_associations('gene', 'gene', rel, id, **core_parser.parse_args())
    
@ns.route('/gene/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GenePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    def get(self, id):
        """
        Returns phenotypes associated with gene
        """
        args = core_parser.parse_args()
        print(args)

        return search_associations('gene', 'phenotype', None, id, **core_parser.parse_args())

@ns.route('/gene/<id>/expressed/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GeneExpressionAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        TODO Returns expression events for a gene
        """

        return search_associations('gene', 'anatomy', None, id, **core_parser.parse_args())

@ns.route('/gene/<id>/function/')
class GeneExpressionAssociations(AbstractGeneAssociationResource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        TODO Returns expression events for a gene
        """

        return search_associations_go('gene', 'goclass', None, id, **core_parser.parse_args())
    
@ns.route('/gene/<id>/pubs/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GenePublicationList(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        TODO Returns expression events for a gene
        """

        # TODO: we don't store this directly
        # could be retrieved by getting all associations and then extracting pubs
        return search_associations('gene', 'publication', None, id, **core_parser.parse_args())
    
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
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with disease
        """

        return search_associations('disease', 'phenotype', None, id, **core_parser.parse_args())

@ns.route('/disease/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a disease
        """
        args = core_parser.parse_args()
        print(args)

        return search_associations('disease', 'gene', None, id, **core_parser.parse_args())

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
    
@ns.route('/disease/<id>/models/')
@api.doc(params={'id': 'CURIE identifier of disease, e.g. OMIM:605543, DOID:678. Equivalent IDs can be used with same results'})
class DiseaseModelAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        TODO Returns models associated with a disease
        """

        # TODO: invert
        return search_associations('model', 'disease', None, id, invert_subject_object=True, **core_parser.parse_args())
    
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
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns anatomical locations associated with a phenotype
        """
        return { 'foo' : 'bar' }

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

@ns.route('/pub/<id>')
class PubObject(Resource):

    @api.expect(core_parser)
    @api.marshal_with(publication)
    def get(self, id):
        """
        TODO Returns publication object
        """
        return { 'id' : 'PMID:1' }
    
@ns.route('/anatomy/<id>')
class AnatomyObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns anatomical entity

        Anatomical entities span ranges from the subcellular (e.g. nucleus) through cells to tissues, organs and organ systems.
        """
        return { 'foo' : 'bar' }

@ns.route('/anatomy/<id>/genes/')
class AnatomyGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between anatomical entity and genes

        Typically encompasses genes expressed in a particular location.
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

@ns.route('/drug/<id>')
class DrugObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(drug)
    def get(self, id):
        """
        TODO Returns drug entity
        """
        return { 'foo' : 'bar' }

@ns.route('/drug/<id>/targets/')
class DrugTargetAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between given drug and targets
        """
        return { 'foo' : 'bar' }

@ns.route('/drug/<id>/interactions/')
class DrugInteractions(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns associations between given drug and interactions

        Interactions can encompass drugs or environments
        """
        return { 'foo' : 'bar' }
    
@ns.route('/chemical/<id>')
class ChemicalObject(Resource):

    @api.expect(core_parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        TODO Returns chemical entity
        """
        return { 'foo' : 'bar' }
    

@ns.route('/genotype/<id>')
class GenotypeObject(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(genotype)
    def get(self, id):
        """
        TODO Returns genotype object
        """
        return { 'foo' : 'bar' }

@ns.route('/genotype/<id>/genotypes/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeGenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns genotypes-genotype associations.

        Genotypes may be related to one another according to the GENO model
        """

        # TODO: invert
        return search_associations('genotype', 'genotype', None, id, **core_parser.parse_args())

@ns.route('/genotype/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypePhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a genotype
        """

        # TODO: invert
        return search_associations('genotype', 'phenotypes', None, id, **core_parser.parse_args())
    
@ns.route('/genotype/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of genotype, e.g. ZFIN:ZDB-FISH-150901-6607'})
class GenotypeGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a genotype
        """

        # TODO: invert
        return search_associations('genotype', 'gene', None, id, **core_parser.parse_args())

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
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns genotypes associated with a variant
        """

        # TODO: invert
        return search_associations('variant', 'genotype', None, id, **core_parser.parse_args())

@ns.route('/variant/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantPhenotypeAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns phenotypes associated with a variant
        """

        # TODO: invert
        return search_associations('variant', 'phenotypes', None, id, **core_parser.parse_args())
    
@ns.route('/variant/<id>/genes/')
@api.doc(params={'id': 'CURIE identifier of variant, e.g. ZFIN:ZDB-ALT-010427-8, ClinVarVariant:39783'})
class VariantGeneAssociations(Resource):

    @api.expect(core_parser)
    @api.marshal_list_with(association_results)
    def get(self, id):
        """
        Returns genes associated with a variant
        """

        # TODO: invert
        return search_associations('variant', 'gene', None, id, **core_parser.parse_args())
    
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
    
    

