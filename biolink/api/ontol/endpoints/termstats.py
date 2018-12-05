import logging

from flask import request
from flask_restplus import Resource
from biolink.api.restplus import api
from ontobio.golr.golr_associations import calculate_information_content

from biolink import USER_AGENT

log = logging.getLogger(__name__)

parser = api.parser()
parser.add_argument('evidence', help="""Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)
                    or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.
                    """)

class InformationContentResource(Resource):

    @api.expect(parser)
    def get(self, subject_category, object_category, subject_taxon):
        """
        Returns information content (IC) for a set of relevant ontology classes.

        ```
        IC = -log2( freq(t) / popSize )
        ```

        Here the frequency and population is calculated for a particular dataset:
        e.g. all human disease-phenotype associations

        """
        args = parser.parse_args()
        return calculate_information_content(
            subject_category=subject_category,
            object_category=object_category,
            subject_taxon=subject_taxon,
            user_agent=USER_AGENT,
            **args
        )


    
    

