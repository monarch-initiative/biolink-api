from pathlib import Path
import json

from biolink.app import app
from biolink.datamodel.mme_serializers import mme_request_marshmallow

from ontobio.model.mme.request import Observed
import pytest

patient_1 = Path(__file__).parent / 'resources' / 'mme' / 'patient1.json'


class TestMmeApi():
    """
    Integration tests for sim endpoints (score, compare, search)
    Note it may be better to mock the ontobio output to create
    more specific tests
    """

    @classmethod
    def setup_class(self):
        app.testing = True
        self.test_client = app.test_client()

    @classmethod
    def teardown_class(self):
        self.test_client = None

    def test_marshmallow_dataclass_conversion(self):
        """
        Test that marshmallow is correctly deserializing
        json into our dataclass model, mostly concerned
        with the Enum conversion
        """
        with open(patient_1, 'r') as patient_1_json:
            patient1 = json.load(patient_1_json)
            mme_request = mme_request_marshmallow.load(patient1)

        assert mme_request.features[0].observed == 'yes'
        assert mme_request.features[0].observed == Observed.yes

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/mme/disease",
            "/api/mme/mouse",
            "/api/mme/zebrafish",
            "/api/mme/nematode",
            "/api/mme/fly"
        ]
    )
    def test_mme_post(self, endpoint):
        with open(patient_1, 'r') as patient_1_json:
            patient1 = json.load(patient_1_json)

        response = self.test_client.post(endpoint, json=patient1)

        # sanity check
        assert response.status_code == 200
        assert response.json['results'][0]['score']['patient'] > 0

    def test_bad_request(self):
        data = {
            "bad-data": 1
        }

        response = self.test_client.post("/api/mme/disease", json=data)
        assert response.status_code == 400
