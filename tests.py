from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health(): assert client.get('/api/health').status_code==200

def test_pages():
    for p in ['/', '/explore', '/solar-system', '/dashboard', '/research', '/about', '/login']: assert client.get(p).status_code==200

def test_biosignature():
    r=client.post('/api/simulate/biosignature',json={'composition':{'O2':0.2,'CH4':0.1}}); assert r.status_code==200 and 'potential_biosignature_evidence' in r.json()

def test_lensing():
    r=client.post('/api/simulate/gravitational-lensing?mass_solar=1&lens_distance_pc=100&source_distance_pc=1000'); assert r.status_code==200

def test_analysis_custom():
    r=client.post('/api/analysis',json={'target':'Synthetic Candidate','data':{'pl_name':'Synthetic Candidate','pl_rade':1.1,'pl_masse':1.2,'pl_eqt':285,'pl_insol':1.0}}); assert r.status_code==200

def test_pagination(): assert client.get('/api/planets?limit=5&offset=0').status_code==200
