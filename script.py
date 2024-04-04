# test_script.py

import os
import json
from datetime import datetime

import requests
from flask import Flask, request
import pandas as pd
from sqlalchemy import create_engine

def fetch_data(url):
    response = requests.get(url)
    return response.json()

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Hello, World!"

    return app

if __name__ == "__main__":
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("OS name:", os.name)
    print("JSON example:", json.dumps({'test': True}))
    app = create_app()
    app.run(debug=True)
