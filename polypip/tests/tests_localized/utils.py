import json
from misc.calculation import calculate

def fetch_data():
    # Imagine fetching and returning data here
    return {'data': 123}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)
