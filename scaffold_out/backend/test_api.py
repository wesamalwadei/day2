import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def asset_data():
    return {
        'asset_id': 'ABC-1234',
        'asset_type': 'Generator',
        'unit': 'Unit 1',
        'location': 'Site A',
        'install_year': 2020,
        'last_inspection': '2023-01-01',
        'operating_hours': 150,
        'status': 'In Service',
        'criticality': 'High',
        'notes': None
    }

def test_create_asset(asset_data):
    response = client.post('/assets', json=asset_data)
    assert response.status_code == 200
    assert response.json()['asset_id'] == asset_data['asset_id']

def test_create_asset_invalid(asset_data):
    asset_data['asset_id'] = 'INVALID'
    response = client.post('/assets', json=asset_data)
    assert response.status_code == 422

def test_list_assets():
    response = client.get('/assets')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_asset(asset_data):
    client.post('/assets', json=asset_data)
    response = client.get(f'/assets/{asset_data['asset_id']}')
    assert response.status_code == 200
    assert response.json()['asset_id'] == asset_data['asset_id']

def test_read_asset_not_found():
    response = client.get('/assets/XYZ-9999')
    assert response.status_code == 404

def test_update_asset(asset_data):
    client.post('/assets', json=asset_data)
    asset_data['status'] = 'Under Maintenance'
    response = client.put(f'/assets/{asset_data['asset_id']}', json=asset_data)
    assert response.status_code == 200
    assert response.json()['status'] == 'Under Maintenance'

def test_update_asset_invalid(asset_data):
    client.post('/assets', json=asset_data)
    asset_data['asset_id'] = 'INVALID'
    response = client.put(f'/assets/{asset_data['asset_id']}', json=asset_data)
    assert response.status_code == 404

def test_delete_asset(asset_data):
    client.post('/assets', json=asset_data)
    response = client.delete(f'/assets/{asset_data['asset_id']}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Asset soft deleted'

def test_delete_asset_not_found():
    response = client.delete('/assets/XYZ-9999')
    assert response.status_code == 404