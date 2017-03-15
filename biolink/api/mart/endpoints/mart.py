import logging

from flask import request
from flask import abort
from flask_restplus import Resource
from biolink.api.restplus import api
from biogolr.golr_associations import bulk_fetch
from biogolr.golr_associations import search_associations
from biogolr.golr_associations import MAX_ROWS
from biolink.datamodel.serializers import compact_association_set

# https://flask-limiter.readthedocs.io/en/stable/
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["200 per day", "50 per hour"]
)

log = logging.getLogger(__name__)

ns = api.namespace('mart', description='Bulk operations')

parser = api.parser()
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID or subset ID')

@ns.route('/gene/<object_category>/<taxon>')
#@limiter.limit("1 per minute")
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of gene, must be of form NCBITaxon:9606'})
class MartGeneAssociationsResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(compact_association_set)
    def get(self, object_category, taxon):
        """
        Bulk download of gene associations.

        NOTE: this route has a limiter on it, you may be restricted in the number of downloads per hour. Use carefully.
        """
        assocs = bulk_fetch(subject_category='gene',
                            object_category=object_category,
                            taxon=taxon,
                            iterate=True)
        return assocs

@ns.route('/case/<object_category>/<taxon>')
#@limiter.limit("1 per minute")
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of case, must be of form NCBITaxon:9606'})
class MartCaseAssociationsResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(compact_association_set)
    def get(self, object_category, taxon):
        """
        Bulk download of case associations.

        NOTE: this route has a limiter on it, you may be restricted in the number of downloads per hour. Use carefully.
        """
        assocs = bulk_fetch(subject_category='case',
                            object_category=object_category,
                            taxon=taxon,
                            iterate=True)
        return assocs

@ns.route('/disease/<object_category>/<taxon>')
#@limiter.limit("1 per minute")
@api.doc(params={'object_category': 'CATEGORY of entity at link OBJECT (target), e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of disease, must be of form NCBITaxon:9606'})
class MartDiseaseAssociationsResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(compact_association_set)
    def get(self, object_category, taxon):
        """
        Bulk download of disease associations.

        NOTE: this route has a limiter on it, you may be restricted in the number of downloads per hour. Use carefully.
        """
        assocs = bulk_fetch(subject_category='disease',
                            object_category=object_category,
                            taxon=taxon,
                            iterate=True)
        return assocs

@ns.route('/labels/<subject_category>/<objet_category>/<taxon>')
@api.doc(params={'subject_category': 'CATEGORY of the subject entity, e.g. gene, phenotype, disease'})
@api.doc(params={'objet_category': 'CATEGORY of the object entity, e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of gene, must be of form NCBITaxon:9606'})
class MartLabelsResource(Resource):
    def get(self, subject_category, objet_category, taxon):
        """
        Bulk download of labels.

        Retrieves the labels of the subjects.
        """
        myArgs = {
            "subject_category": subject_category,
            "object_category": objet_category,
            "subject_taxon": taxon,
            "rows": MAX_ROWS,
            "facet_on": "off",
            "select_fields": ["subject", "subject_label"],
            "iterate": True
        }
        return search_associations(**myArgs)
