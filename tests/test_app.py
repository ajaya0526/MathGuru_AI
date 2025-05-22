import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"MathGuru" in response.data  # adjust based on actual homepage content

def test_ocr_route(client):
    # This test simulates accessing the OCR endpoint without a file
    response = client.post('/process', data={})
    assert response.status_code in [200, 400]
