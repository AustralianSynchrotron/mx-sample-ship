import json


def arrival_data(dewar):
    data = {
        'type': 'UPDATE_DEWAR',
        'dewar': dewar['name'],
        'update': {
            'onsite': True
        }
    }
    return json.dumps(data)
