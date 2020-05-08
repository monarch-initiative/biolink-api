from biolink.app import app
from biolink.api.sim.endpoints.owlsim import get_owlsim_api


class TestSimApi():
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

    def test_search(self):
        response = self.test_client.get('/api/sim/search?id=HP:0000739&id=HP:0000740')
        assert response.status_code == 200
        assert len(response.json['matches']) > 0
        assert {query['id'] for query in response.json['query']['ids']} == {'HP:0000739', 'HP:0000740'}

    def test_search_w_taxon(self):
        response = self.test_client.get('/api/sim/search?id=HP:0000739&id=HP:0000740&taxon=9606')
        assert response.status_code == 200
        assert len(response.json['matches']) > 0
        assert {match['taxon']['id'] for match in response.json['matches']} == {'NCBITaxon:9606'}

    def test_compare_post(self):
        data = {
            'reference_ids': ['HP:0000739', 'HP:0001831'],
            'query_ids': [
                ['HP:0000716', 'HP:0011307'],
                ['HP:0001004']
            ]
        }
        response = self.test_client.post('/api/sim/compare', json=data)
        assert response.status_code == 200
        assert len(response.json['matches']) > 0

    def test_compare_post_genes(self):
        data = {
            'is_feature_set': False,
            'reference_ids': ['HP:0000739', 'HP:0001831'],
            'query_ids': [
                ['HGNC:6407'],
                ['HGNC:12373']
            ]
        }
        response = self.test_client.post('/api/sim/compare', json=data)
        assert response.status_code == 200
        assert len(response.json['matches']) > 0

    def test_score_post(self):
        data = {
            'id': 'testID',
            'features': [
                {
                    'id': 'HP:0000739',
                    'isPresent': True
                },
                {
                    'id': 'HP:0011307',
                    'isPresent': False
                },
            ]
        }
        response = self.test_client.post('/api/sim/score', json=data)
        assert response.status_code == 200
        assert response.json['simple_score'] > 0

    def test_owlsim_singleton(self):
        """
        test that two calls to get_owlsim_api()
        get the same object
        """
        foo = get_owlsim_api()
        bar = get_owlsim_api()
        assert foo is bar
