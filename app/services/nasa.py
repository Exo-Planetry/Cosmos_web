import asyncio, json
from typing import Any, Dict, List
import httpx
from app.core.cache import get, set

FIELDS=['pl_name','hostname','pl_orbper','pl_rade','pl_masse','pl_eqt','pl_insol','pl_orbeccen','pl_orbincl','pl_trandep','pl_trandur','pl_orbsmax','st_lum','st_teff','st_mass','sy_dist','disc_facility','pl_bmassprov','pl_dens','pl_ratdor']
CURATED=[
 {'pl_name':'Kepler-22 b','pl_orbper':289.86,'pl_rade':2.38,'pl_eqt':262.0,'pl_insol':1.11},
 {'pl_name':'TOI-700 d','pl_orbper':37.42,'pl_rade':1.14,'pl_eqt':269.0,'pl_insol':0.85},
 {'pl_name':'TRAPPIST-1 e','pl_orbper':6.10,'pl_rade':0.92,'pl_eqt':251.0,'pl_insol':0.66},
 {'pl_name':'K2-18 b','pl_orbper':32.94,'pl_rade':2.61,'pl_eqt':265.0,'pl_insol':1.0},
 {'pl_name':'Kepler-186 f','pl_orbper':129.94,'pl_rade':1.17,'pl_eqt':188.0,'pl_insol':0.32},
]

async def _get(url,params=None,timeout=15):
    async with httpx.AsyncClient(timeout=timeout,headers={'User-Agent':'COSMOS/5.0'}) as client:
        r=await client.get(url,params=params); r.raise_for_status(); return r.json()

def _norm(rows):
    for row in rows:
        for k,v in list(row.items()):
            if k!='pl_name' and v not in (None,''):
                try: row[k]=float(v)
                except: pass
    return rows

async def search_target_async(name:str):
    q=(name or '').strip()
    if not q:return {'status':'NotFound','source':'NASA Exoplanet Archive','message':'Target name is required'}
    key='nasa:'+q.lower(); cached=get(key)
    if cached:return cached
    sql="select "+','.join(FIELDS)+" from ps where pl_name like '%"+q.replace("'","''")+"%' and default_flag=1"
    try:
        rows=_norm(await _get('https://exoplanetarchive.ipac.caltech.edu/TAP/sync',{'query':sql,'format':'json'}))
        if not rows:return {'status':'NotFound','source':'NASA Exoplanet Archive','message':'No catalog record found'}
        data=rows[0]; result={'status':'Success','source':'NASA Exoplanet Archive TAP','data':data,'data_status':'Catalogued','missing_fields':[k for k in FIELDS if data.get(k) is None]}; return set(key,result)
    except Exception as exc:return {'status':'Unavailable','source':'NASA Exoplanet Archive','message':str(exc)}

def search_target(name:str):
    return asyncio.run(search_target_async(name))

async def mast_search_async(target:str):
    payload={'service':'Mast.Caom.Filtered','params':{'columns':'*','filters':[{'paramName':'target_name','values':[target]}]},'format':'json','pagesize':50}
    try:
        result=await _get('https://mast.stsci.edu/api/v0/invoke',payload,15)
        return {'status':'Success','source':'MAST CAOM','data':result.get('data',[]),'data_status':'Archive metadata'}
    except Exception as exc:return {'status':'Unavailable','source':'MAST CAOM','message':str(exc)}

def mast_search(target): return asyncio.run(mast_search_async(target))
def mast_search(target): return asyncio.run(mast_search_async(target))
def known_targets(): return CURATED

async def get_all_targets_async(limit=500):
    key = f'nasa:all:{limit}'
    cached = get(key)
    if cached: return cached
    
    sql = "select " + ','.join(FIELDS) + f" from ps where default_flag=1 order by disc_year desc"
    try:
        # Note: NASA TAP sync only allows top N via specific clauses, but for generic we can just fetch and slice.
        # Actually, TOP N works in Oracle/ADQL depending on the TAP provider. ADQL supports TOP N.
        sql = f"select TOP {limit} " + ','.join(FIELDS) + " from ps where default_flag=1 order by disc_year desc"
        rows = _norm(await _get('https://exoplanetarchive.ipac.caltech.edu/TAP/sync', {'query': sql, 'format': 'json'}))
        if not rows: return {'status': 'Error', 'message': 'No records found'}
        result = {'status': 'Success', 'source': 'NASA Exoplanet Archive', 'data': rows}
        return set(key, result)
    except Exception as exc:
        return {'status': 'Unavailable', 'message': str(exc)}

def get_all_targets(limit=500):
    return asyncio.run(get_all_targets_async(limit))
