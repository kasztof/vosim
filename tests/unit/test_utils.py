import base64
from vosim.utils import get_network
from conftest import test_data_path


def test_get_network(test_data_path):
    data = open(test_data_path, 'r').read()
    data_bytes = data.encode("utf-8")
    encoded = base64.b64encode(data_bytes)
    correct = [
        {'data': {'id': 0, 'label': 0, 'score': 2}},
        {'data': {'id': 1, 'label': 1, 'score': 2}},
        {'data': {'id': 2, 'label': 2, 'score': 2}},
        {'data': {'id': 3, 'label': 3, 'score': 2}},
        {'data': {'source': 0, 'target': 2}},
        {'data': {'source': 1, 'target': 2}},
        {'data': {'source': 0, 'target': 3}},
        {'data': {'source': 1, 'target': 3}}
    ]
    assert get_network('data:text/csv;base64,MSwyCjEsMwoxLDQKMiwzCjIsNA==') == correct

