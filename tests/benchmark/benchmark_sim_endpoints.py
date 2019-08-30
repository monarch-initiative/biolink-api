"""
pip install pytest-benchmark
pytest tests/unit/benchmark_sim_endpoints.py
"""

import requests

app_base = 'http://127.0.0.1:8888'


def search_two():
    req = requests.get(app_base + '/api/sim/search?id=HP:0000739&id=HP:0000740')
    return req


def search_ten():
    params = {
        'id': [
            'HP:0002905',
            'HP:0001265',
            'HP:0000684',
            'HP:0000518',
            'HP:0003472',
            'HP:0000739',
            'HP:0006297',
            'HP:0010766',
            'HP:0011458',
            'HP:0008227'
        ]
    }
    req = requests.get(app_base + '/api/sim/search', params=params)
    return req


def search_twenty():
    params = {
        'id': [
            'HP:0002905',
            'HP:0001265',
            'HP:0000684',
            'HP:0000518',
            'HP:0003472',
            'HP:0000739',
            'HP:0006297',
            'HP:0010766',
            'HP:0011458',
            'HP:0008227',
            'HP:0100749',
            'HP:0000852',
            'HP:0001513',
            'HP:0000737',
            'HP:0003401',
            'HP:0030057',
            'HP:0002094',
            'HP:0003909',
            'HP:0100660',
            'HP:0000311'
        ]
    }
    req = requests.get(app_base + '/api/sim/search', params=params)
    return req


def search_forty():
    params = {
        'id': [
            'HP:0002905',
            'HP:0001265',
            'HP:0000684',
            'HP:0000518',
            'HP:0003472',
            'HP:0000739',
            'HP:0006297',
            'HP:0010766',
            'HP:0011458',
            'HP:0008227',
            'HP:0100749',
            'HP:0000852',
            'HP:0001513',
            'HP:0000737',
            'HP:0003401',
            'HP:0030057',
            'HP:0002094',
            'HP:0003909',
            'HP:0100660',
            'HP:0010049',
            'HP:0003761',
            'HP:0000470',
            'HP:0000509',
            'HP:0000639',
            'HP:0011001',
            'HP:0000293',
            'HP:0000716',
            'HP:0001657',
            'HP:0012049',
            'HP:0003034',
            'HP:0003456',
            'HP:0003165',
            'HP:0004322',
            'HP:0002901',
            'HP:0003739',
            'HP:0001156',
            'HP:0000824',
            'HP:0003394',
            'HP:0002199',
            'HP:0005700',
            'HP:0005280',
            'HP:0000311'
        ]
    }
    req = requests.get(app_base + '/api/sim/search', params=params)
    return req


def test_two(benchmark):
    response = benchmark.pedantic(search_two, rounds=15, iterations=2)
    assert response.status_code == 200
    assert len(response.json()['matches']) > 0


def test_ten(benchmark):
    response = benchmark.pedantic(search_ten, rounds=15, iterations=2)
    assert response.status_code == 200
    assert len(response.json()['matches']) > 0


def test_twenty(benchmark):
    response = benchmark.pedantic(search_twenty, rounds=15, iterations=2)
    assert response.status_code == 200
    assert len(response.json()['matches']) > 0


def test_forty(benchmark):
    response = benchmark.pedantic(search_forty, rounds=15, iterations=2)
    assert response.status_code == 200
    assert len(response.json()['matches']) > 0
