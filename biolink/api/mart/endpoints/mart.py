import logging

from flask import request
from flask import abort
from flask_restplus import Resource
from biolink.api.restplus import api
from ontobio.golr.golr_associations import bulk_fetch
from ontobio.golr.golr_associations import search_associations
from ontobio.golr.golr_associations import MAX_ROWS
from biolink.datamodel.serializers import compact_association_set
from ontobio.vocabulary.relations import HomologyTypes
from biolink import USER_AGENT

# https://flask-limiter.readthedocs.io/en/stable/
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

homolog_rel = HomologyTypes.Homolog.value
paralog_rel = HomologyTypes.Paralog.value
ortholog_rel = HomologyTypes.Ortholog.value

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["200 per day", "50 per hour"]
)

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID or subset ID')

#@limiter.limit("1 per minute")
@api.doc(params={'object_category': 'Category of entity at link Object (target), e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of gene, must be of form NCBITaxon:9606'})
class MartGeneAssociationsResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(compact_association_set)
    def get(self, object_category, taxon):
        """
        Bulk download of gene associations.

        NOTE: this route has a limiter on it, you may be restricted in the number of downloads per hour. Use carefully.
        """
        assocs = bulk_fetch(
            subject_category='gene',
            object_category=object_category,
            taxon=taxon,
            user_agent=USER_AGENT
        )
        return assocs

#@limiter.limit("1 per minute")
@api.doc(params={'object_category': 'Category of entity at link Subject (target), e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of case, must be of form NCBITaxon:9606'})
class MartCaseAssociationsResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(compact_association_set)
    def get(self, object_category, taxon):
        """
        Bulk download of case associations.

        NOTE: this route has a limiter on it, you may be restricted in the number of downloads per hour. Use carefully.
        """

        # TODO temporary workaround for # https://github.com/monarch-initiative/monarch-app/issues/1448
        if taxon == "NCBITaxon:9606":
            taxon = None

        assocs = bulk_fetch(
            subject_category='case',
            object_category=object_category,
            taxon=taxon,
            user_agent=USER_AGENT
        )
        return assocs

#@limiter.limit("1 per minute")
@api.doc(params={'object_category': 'Category of entity at link Object (target), e.g. phenotype, disease'})
@api.doc(params={'taxon': 'taxon of disease, must be of form NCBITaxon:9606'})
class MartDiseaseAssociationsResource(Resource):

    @api.expect(parser)
    #@api.marshal_list_with(compact_association_set)
    def get(self, object_category, taxon):
        """
        Bulk download of disease associations.

        NOTE: this route has a limiter on it, you may be restricted in the number of downloads per hour. Use carefully.
        """

        # TODO temporary workaround for # https://github.com/monarch-initiative/monarch-app/issues/1448
        if taxon == "NCBITaxon:9606":
            taxon = None

        assocs = bulk_fetch(
            subject_category='disease',
            object_category=object_category,
            taxon=taxon,
            user_agent=USER_AGENT
        )
        return assocs

@api.doc(params={'taxon1': 'subject taxon, e.g. NCBITaxon:9606'})
@api.doc(params={'taxon2': 'object taxon, e.g. NCBITaxon:9606'})
class MartParalogAssociationsResource(Resource):

    def get(self, taxon1, taxon2):
        """
        Bulk download of paralogs
        """
        assocs = bulk_fetch(
            subject_category='gene',
            object_category='gene',
            relation=paralog_rel,
            taxon=taxon1,
            object_taxon=taxon2,
            user_agent=USER_AGENT
        )
        return assocs

@api.doc(params={'taxon1': 'subject taxon, e.g. NCBITaxon:9606'})
@api.doc(params={'taxon2': 'object taxon, e.g. NCBITaxon:10090'})
class MartOrthologAssociationsResource(Resource):

    def get(self, taxon1, taxon2):
        """
        Bulk download of orthologs
        """
        assocs = bulk_fetch(
            subject_category='gene',
            object_category='gene',
            relation=ortholog_rel,
            taxon=taxon1,
            object_taxon=taxon2,
            user_agent=USER_AGENT
        )
        return assocs