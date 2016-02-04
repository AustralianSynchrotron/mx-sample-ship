from mxsampleship.utils import arrival_data
import json


def test_arrival_data():
    expected = {'type': 'UPDATE_DEWAR', 'dewar': '123', 'update': {'onsite': True}}
    data = arrival_data({'name': '123'})
    assert json.loads(data) == expected
