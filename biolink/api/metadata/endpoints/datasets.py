from biolink.api.restplus import api
from flask_restplus import Resource
from biolink.settings import get_biolink_config
from scigraph.scigraph_util import SciGraph


scigraph = SciGraph(get_biolink_config()['scigraph_data']['url'])


class MetadataForDatasets(Resource):

    def get(self):
        """
        Get metadata for all datasets from SciGraph
        """

        return scigraph.get_datasets()
