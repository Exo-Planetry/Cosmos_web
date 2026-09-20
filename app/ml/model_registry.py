import json
from pathlib import Path
REGISTRY=Path(__file__).resolve().parents[2]/'models'/'registry.json'
def list_models():
    return json.loads(REGISTRY.read_text()) if REGISTRY.exists() else []
def register(name,version,kind,metrics=None,status='research'):
    rows=list_models(); rows.append({'name':name,'version':version,'kind':kind,'metrics':metrics or {},'status':status}); REGISTRY.parent.mkdir(exist_ok=True); REGISTRY.write_text(json.dumps(rows,indent=2)); return rows[-1]
