import csv
from pathlib import Path
from app.db.database import SessionLocal, init_db
from app.db.models import Planet
from sqlalchemy import select
BASE=Path(__file__).resolve().parents[2]

def seed_reference():
    init_db()
    path=BASE/'data'/'reference'/'transit_catalog.csv'
    if not path.exists(): return 0
    with path.open(newline='',encoding='utf-8',errors='ignore') as f: rows=csv.DictReader(f); count=0
    # reopen because DictReader is lazy
    with path.open(newline='',encoding='utf-8',errors='ignore') as f:
        for row in csv.DictReader(f):
            name=(row.get('pl_name') or '').strip()
            if not name: continue
            with SessionLocal() as db:
                if db.scalar(select(Planet.id).where(Planet.name==name)): continue
                def fl(k):
                    try:return float(row.get(k)) if row.get(k) not in ('',None) else None
                    except:return None
                db.add(Planet(name=name,radius_earth=fl('pl_rade'),mass_earth=None,orbital_period_days=fl('pl_orbper'),equilibrium_temp_k=None,stellar_flux=None,source='NASA reference snapshot',payload_json=str(dict(row))))
                db.commit(); count+=1
            if count>=500: break
    return count
