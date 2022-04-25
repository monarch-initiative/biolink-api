from pprint import pprint

import pytest
from biolink.app import app
from biolink.api.sim.endpoints.owlsim import get_owlsim_api


class TestOntolIdentifier():
    """
    Integration tests for ontol identifier endpoint, using labeler as a comparison.

    Specifically, does a sanity check against identifier, then determines if we
    can (somewhat) losslessly map a set of labels to IDs and back
    """

    @classmethod
    def setup_class(self):
        app.testing = True
        self.test_client = app.test_client()

    @classmethod
    def teardown_class(self):
        self.test_client = None
    
    def test_sample_identifier(self):
        response = self.test_client.get('/api/ontol/identifier?label=Mus%20musculus')
        assert response.status_code == 200

        # todo: assert we have results, and that the response matches a known entry
        assert len(response.json.items()) > 0
        assert (
            response.json == {
                "Mus musculus": [
                    "NCBITaxon:10090",
                    "OBO:FBsp_00000276",
                    "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C45247",
                    "VTO:0014661"
                ]
            }
        )

    @pytest.mark.xfail(reason="/ontol/labeler returns just one result, so it can't be onto with /ontol/identifier")
    def test_label_id_nonlossy(self):
        labels = [
            "Sus scrofa",
            "Drosophila melanogaster",
            "Homo sapiens",
            "Mus musculus",
            "Bos taurus",
            "Saccharomyces cerevisiae S288C",
            "Xenopus tropicalis",
            "Danio rerio",
            "Gallus gallus",
            "Anolis carolinensis",
            "Canis lupus familiaris",
            "Felis catus",
            "Macaca mulatta",
            "Monodelphis domestica",
            "Ornithorhynchus anatinus",
            "Pan troglodytes",
            "Rattus norvegicus",
            "Takifugu rubripes",
            "Equus caballus"
        ]

        response = self.test_client.post('/api/ontol/identifier', data={'label': labels})
        pprint(response.json)

        assert response.status_code == 200

        # todo: assert we have results
        assert len(response.json.items()) > 0

        # extract the first ID and its label from each result
        id_set = {ids[0]: label for label, ids in response.json.items()}

        # produce a query of IDs to labels using the /ontol/labels/
        response = self.test_client.get(
            '/api/ontol/labeler/?%s' % "&".join("id=%s" % x for x in id_set.keys())
        )
        pprint(response.json)

        # gather the results and compare to the initial set of labels
        orignal_set = set(labels)
        response_set = set(response.json.values()) 

        assert orignal_set == response_set, (
            "Response labels and originals don't match! difference: %s" % orignal_set.difference(response_set)
        )
