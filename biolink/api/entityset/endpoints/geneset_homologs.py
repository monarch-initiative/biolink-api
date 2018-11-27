import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association_results
from ontobio.golr.golr_associations import search_associations, GolrFields
from ontobio.vocabulary.relations import HomologyTypes

from biolink.api.restplus import api
from biolink import USER_AGENT

MAX_ROWS=10000

log = logging.getLogger(__name__)

homology_types = [
    HomologyTypes.Homolog.value,
    HomologyTypes.Paralog.value,
    HomologyTypes.Ortholog.value,
    HomologyTypes.LeastDivergedOrtholog.value,
    HomologyTypes.InParalog.value,
    HomologyTypes.OutParalog.value,
    HomologyTypes.Ohnolog.value,
    HomologyTypes.Xenolog.value
]

parser = api.parser()
parser.add_argument('subject', required=True, action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('relation', choices=homology_types, help='relation based on which to fetch associations. Default: {} ({})'.format(HomologyTypes.Homolog.value, HomologyTypes.Homolog.name), default=HomologyTypes.Homolog.value)

class EntitySetHomologs(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association_results)
    def get(self):
        """
        Returns homology associations for a given input set of genes
        """
        args = parser.parse_args()
        subjects = args.get('subject')
        del args['subject']

        M=GolrFields()
        results = search_associations(
            subjects=subjects,
            select_fields=[M.SUBJECT, M.RELATION, M.OBJECT],
            use_compact_associations=True,
            rows=MAX_ROWS,
            facet_fields=[],
            user_agent=USER_AGENT,
            **args
        )
        return results
