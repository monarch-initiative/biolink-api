import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association, gene, drug, genotype, allele
#import biolink.datamodel.serializers
from biolink.api.restplus import api
from biolink.util.golr_associations import get_associations
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bio', description='Bio Objects')

parser = api.parser()
#parser.add_argument('subject', help='SUBJECT id, e.g. NCBIGene:84570. Includes inferred by default')
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')
#parser.add_argument('object', help='OBJECT id, e.g. HP:0011927. Includes inferred by default')


@ns.route('/gene/<id>')
@api.doc(params={'id': 'id, e.g. NCBIGene:84570'})
class GeneObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(gene)
    def get(self, id):
        """
        Returns gene
        """
        return { 'foo' : 'bar' }

@ns.route('/gene/<id>/phenotypes/')
@api.doc(params={'id': 'CURIE identifier of gene, e.g. NCBIGene:4750. Equivalent IDs can be used with same results'})
class GenePhenotypeAssociations(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of associations
        """
        args = parser.parse_args()
        print(args)

        return get_associations('gene', 'phenotype', args, args.get('id'))
    
@ns.route('/geneproduct/<id>')
class GeneproductObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }
    
@ns.route('/disease/<id>')
class DiseaseObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }

@ns.route('/phenotype/<id>')
class PhenotypeObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }
    

@ns.route('/goterm/<id>')
class GotermObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }
    

@ns.route('/anatomy/<id>')
class AnatomyObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }

@ns.route('/anatomy/<id>/genes/')
class AnatomyGeneAssociations(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of associations
        """
        return { 'foo' : 'bar' }
    

@ns.route('/environment/<id>')
class EnvironmentObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }
    

@ns.route('/drug/<id>')
class DrugObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(drug)
    def get(self, id):
        """
        Returns list of associations
        """
        return { 'foo' : 'bar' }

@ns.route('/drug/<id>/targets/')
class DrugTargetAssociations(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of associations
        """
        return { 'foo' : 'bar' }
    

@ns.route('/chemical/<id>')
class ChemicalObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }
    

@ns.route('/genotype/<id>')
class GenotypeObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(genotype)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }
    

@ns.route('/allele/<id>')
class AlleleObject(Resource):

    @api.expect(parser)
    @api.marshal_list_with(allele)
    def get(self, id):
        """
        Returns list of alleles
        """
        return { 'foo' : 'bar' }
    

@ns.route('/variant/<id>')
class VariantObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }

@ns.route('/sequence_feature/<id>')
class VariantObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }


@ns.route('/patient/<id>')
class ParentObject(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(association)
    def get(self, id):
        """
        Returns list of objects
        """
        return { 'foo' : 'bar' }


