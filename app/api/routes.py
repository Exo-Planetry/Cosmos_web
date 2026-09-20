import asyncio, json, uuid
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from app.core.config import APP_VERSION, MAX_UPLOAD_BYTES
from app.core.limits import check_rate_limit
from app.core.security import create_token, hash_password, require_role, require_user, verify_password, current_user
from app.db.database import SessionLocal
from app.db.models import Planet
from app.db.repository import *
from app.schemas.api import *
from app.services.nasa import known_targets, mast_search_async, search_target_async
from app.science.analysis import analyze
from app.science.transit import analyze_transit
from app.science.orbit import keplerian_rv
from app.science.imaging import analyze_imaging
from app.science.atmosphere import analyze_atmosphere
from app.science.lensing import einstein_angle
from app.services.report import render_report, render_pdf
from app.ml.anomaly import CandidateAnomalyDetector
from app.ml.uncertainty import bootstrap_mean
from app.ml.active_learning import uncertainty_priority
from app.ml.model_registry import list_models
import secrets

router=APIRouter(prefix='/api')

def _uid(request):
    u=current_user(request); return u.get('sub') if u else None

@router.get('/health')
async def health(): return {'status':'ok','service':'COSMOS','version':APP_VERSION}

@router.post('/auth/register')
async def register(req:RegisterRequest):
    if user_by_email(req.email): raise HTTPException(409,'Email already registered')
    role=req.role if req.role in {'researcher','admin','guest'} else 'researcher'
    u=ensure_user(req.email,hash_password(req.password),req.display_name,role); verification=secrets.token_urlsafe(24); set_verification_token(u.id,verification); return {'status':'Success','user_id':u.id,'token':create_token(u.id,u.role),'verification_token':verification,'note':'In production, deliver verification_token through email.'}

@router.post('/auth/login')
async def login(req:LoginRequest):
    u=user_by_email(req.email)
    if not u or not verify_password(req.password,u.password_hash): raise HTTPException(401,'Invalid email or password')
    return {'status':'Success','token':create_token(u.id,u.role),'user':{'id':u.id,'email':u.email,'display_name':u.display_name,'role':u.role}}

@router.get('/auth/me')
async def me(request:Request):
    u=require_user(request); row=user_by_id(u['sub']); return {'id':row.id,'email':row.email,'display_name':row.display_name,'role':row.role}

@router.post('/auth/verify/{token}')
async def verify(token:str):
    if not verify_user_token(token): raise HTTPException(400,'Invalid verification token')
    return {'status':'Success','message':'Email verified'}

@router.post('/auth/password-reset/request')
async def reset_request(req:LoginRequest):
    token=secrets.token_urlsafe(24); ok=set_reset_token(req.email,token); return {'status':'Success','reset_token':token if ok else None,'note':'In production, deliver reset_token through email.'}

@router.post('/auth/password-reset/{token}')
async def reset(token:str,req:LoginRequest):
    if not reset_password(token,hash_password(req.password)): raise HTTPException(400,'Invalid reset token')
    return {'status':'Success','message':'Password reset'}

@router.get('/targets')
async def targets(query:Optional[str]=None,limit:int=20,offset:int=0):
    limit=min(max(limit,1),100); offset=max(offset,0)
    if query:
        r=await search_target_async(query); return r
    return {'status':'Success','data':known_targets()[offset:offset+limit],'total':len(known_targets()),'limit':limit,'offset':offset,'source':'COSMOS curated catalog'}

@router.get('/targets/{name:path}')
async def target(name:str):
    result=await search_target_async(name)
    if result.get('status')!='Success': raise HTTPException(404,result.get('message','Target not found'))
    await asyncio.to_thread(upsert_planet,result['data'],result.get('source','NASA')); return result

@router.get('/mast/{target_name:path}')
async def mast(target_name:str): return await mast_search_async(target_name)

@router.post('/analysis')
async def create_analysis(req:AnalysisRequest,request:Request):
    user=_uid(request); target_name=req.target or (req.data or {}).get('pl_name') or 'Custom Target'; payload=req.model_dump(exclude_none=True)
    try:
        result=await asyncio.to_thread(analyze,target_name,payload)
        result['ml_screening']=await asyncio.to_thread(CandidateAnomalyDetector().score,result.get('target_data',{}))
        aid=await asyncio.to_thread(save_analysis,target_name,result,user); result['provenance']['analysis_id']=aid; await asyncio.to_thread(save_model_run,aid,'cosmos-evidence-baseline','1.0.0',{}); await asyncio.to_thread(save_observation,target_name,result.get('data_source','COSMOS'),'multi-method','Catalogued' if 'NASA' in result.get('data_source','') else 'User supplied',result.get('provenance',{}))
        if user: await asyncio.to_thread(log_activity,user,'analysis_created',target_name)
        return result
    except ValueError as exc: raise HTTPException(400,str(exc))
    except Exception as exc: raise HTTPException(500,f'Analysis failed: {exc}')

@router.get('/analysis')
async def analyses(request:Request,user_id:Optional[str]=None,limit:int=20,offset:int=0):
    uid=_uid(request); requested=uid or user_id; limit=min(max(limit,1),100); offset=max(offset,0); return {'status':'Success','data':await asyncio.to_thread(recent_analyses,requested,limit,offset),'total':await asyncio.to_thread(count_analyses,requested),'limit':limit,'offset':offset}

@router.get('/analysis/{aid}')
async def analysis(aid:str):
    result=await asyncio.to_thread(get_analysis,aid)
    if not result: raise HTTPException(404,'Analysis not found')
    return result

@router.get('/analysis/{aid}/report',response_class=HTMLResponse)
async def report(aid:str):
    result=await asyncio.to_thread(get_analysis,aid)
    if not result: raise HTTPException(404,'Analysis not found')
    return HTMLResponse(render_report(result))

@router.post('/upload')
async def upload(request:Request,file:UploadFile=File(...)):
    filename=file.filename or 'observation'; ext=Path(filename).suffix.lower()
    if ext not in {'.csv','.fits','.fit','.fz'}: raise HTTPException(400,'Only CSV and FITS files are supported.')
    content=await file.read()
    if len(content)>MAX_UPLOAD_BYTES: raise HTTPException(413,f'File exceeds {MAX_UPLOAD_BYTES//(1024*1024)} MB limit.')
    with NamedTemporaryFile(delete=False,suffix=ext) as tmp: tmp.write(content); path=tmp.name
    try:
        result=await asyncio.to_thread(analyze,filename,{'target':filename,'file_path':path}); user=_uid(request); await asyncio.to_thread(save_analysis,result['target_name'],result,user); return result
    finally: Path(path).unlink(missing_ok=True)

@router.post('/simulate/transit')
async def sim_transit(req:SimulationRequest): return analyze_transit(req.values)
@router.post('/simulate/radial-velocity')
async def sim_rv(req:SimulationRequest): return keplerian_rv(list(range(len(req.values))),req.values)
@router.post('/simulate/direct-imaging')
async def sim_imaging(req:SimulationRequest): return analyze_imaging(req.values)
@router.post('/simulate/biosignature')
async def sim_bio(req:AtmosphereRequest): return analyze_atmosphere(req.composition)
@router.post('/simulate/gravitational-lensing')
async def sim_lensing(mass_solar:float=1.0,lens_distance_pc:float=100.0,source_distance_pc:float=1000.0): return einstein_angle(mass_solar,lens_distance_pc,source_distance_pc)
@router.post('/uncertainty')
async def uncertainty(req:SimulationRequest): return bootstrap_mean(req.values)
@router.post('/active-learning/priority')
async def active_learning_priority(prediction:float,model_uncertainty:float): return uncertainty_priority(prediction,model_uncertainty)
@router.get('/models')
async def models(): return {'status':'Success','data':list_models()}
@router.get('/analytics')
async def analytics(request:Request): return {'status':'Success','data':await asyncio.to_thread(summary,_uid(request))}

@router.get('/analysis/{aid}/csv')
async def report_csv(aid:str):
    from fastapi.responses import Response
    data=await asyncio.to_thread(analysis_csv,aid)
    if data is None: raise HTTPException(404,'Analysis not found')
    return Response(data,media_type='text/csv',headers={'Content-Disposition':f'attachment; filename=cosmos-{aid}.csv'})

@router.get('/analysis/{aid}/pdf')
async def report_pdf(aid:str):
    from fastapi.responses import Response
    result=await asyncio.to_thread(get_analysis,aid)
    if not result: raise HTTPException(404,'Analysis not found')
    return Response(await asyncio.to_thread(render_pdf,result),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename=cosmos-{aid}.pdf'})

@router.get('/analysis/{aid}/public')
async def public_report(aid:str):
    result=await asyncio.to_thread(get_analysis,aid)
    if not result: raise HTTPException(404,'Analysis not found')
    return {'status':'Success','public_url':f'/api/public/analysis/{result.get("provenance",{}).get("analysis_id",aid)}','data':result}

@router.get('/public/analysis/{token}')
async def public_analysis_route(token:str):
    result=await asyncio.to_thread(public_analysis,token)
    if not result: raise HTTPException(404,'Public analysis not found')
    return {'status':'Success','data':result,'read_only':True}

@router.get('/analysis/target/{target_name:path}/trend')
async def trend(target_name:str): return {'status':'Success','data':await asyncio.to_thread(analysis_trend,target_name)}

@router.post('/analysis/batch')
async def batch(req:CompareRequest,request:Request):
    if len(req.targets)>6: raise HTTPException(400,'Maximum six targets per batch')
    out=[]
    for name in req.targets:
        try:
            r=await asyncio.to_thread(analyze,name,{'target':name}); out.append({'target':name,'result':r})
        except Exception as exc: out.append({'target':name,'status':'Failed','message':str(exc)})
    return {'status':'Success','data':out}

@router.get('/solar-system/position/{planet_name}')
async def solar_position(planet_name:str):
    # Visualization-grade heliocentric phase. Astropy is used for the timestamp;
    # precise ephemerides require an external ephemeris service/kernel.
    from datetime import datetime, timezone
    import math
    periods={'Mercury':87.97,'Venus':224.7,'Earth':365.25,'Mars':687,'Jupiter':4332.6,'Saturn':10759,'Uranus':30687,'Neptune':60190}
    name=next((k for k in periods if k.lower()==planet_name.lower()),None)
    if not name: raise HTTPException(404,'Solar System planet not found')
    now=datetime.now(timezone.utc); days=(now-datetime(2000,1,1,tzinfo=timezone.utc)).total_seconds()/86400; phase=(days/periods[name])*2*math.pi; return {'status':'Success','planet':name,'timestamp_utc':now.isoformat(),'normalized_heliocentric_position':{'x':math.cos(phase),'z':math.sin(phase)},'data_status':'Visualization ephemeris approximation','note':'Use a validated ephemeris kernel/service for precision astrometry.'}

@router.get('/solar-system/planets')
async def solar_planets():
    rows=[('Mercury',0.055,0.383,87.97,167),('Venus',0.815,0.949,224.7,464),('Earth',1,1,365.25,288),('Mars',0.107,0.532,687,210),('Jupiter',317.8,11.21,4332.6,165),('Saturn',95.2,9.45,10759,134),('Uranus',14.5,4.01,30687,76),('Neptune',17.1,3.88,60190,72)]
    from app.science.orbit import planet_physics
    return {'status':'Success','data':[{'name':n,'mass_earth':m,'radius_earth':r,'orbital_period_days':p,'temperature_k':t,'physics':planet_physics(r,m,p,1)} for n,m,r,p,t in rows]}

@router.get('/planets')
async def planets(query:Optional[str]=None,limit:int=20,offset:int=0):
    limit=min(max(limit,1),100); offset=max(offset,0); return {'status':'Success','data':await asyncio.to_thread(list_planets,query,limit,offset),'total':await asyncio.to_thread(count_planets,query),'limit':limit,'offset':offset}

@router.post('/planets')
async def create_planet(data:dict,request:Request):
    require_role(request,'researcher','admin'); p=await asyncio.to_thread(upsert_planet,data,'COSMOS user'); return {'status':'Success','id':p.id,'name':p.name}

@router.put('/planets/{planet_id}')
async def update_planet(planet_id:int,data:dict,request:Request):
    require_role(request,'admin','researcher')
    with SessionLocal() as db:
        p=db.get(Planet,planet_id)
        if not p: raise HTTPException(404,'Planet not found')
        payload=json.loads(p.payload_json); payload.update(data); payload['pl_name']=payload.get('pl_name') or p.name
    p=await asyncio.to_thread(upsert_planet,payload,'COSMOS user'); return {'status':'Success','id':p.id,'name':p.name}

@router.delete('/planets/{planet_id}')
async def delete_planet(planet_id:int,request:Request):
    require_role(request,'admin')
    with SessionLocal() as db:
        p=db.get(Planet,planet_id)
        if not p: raise HTTPException(404,'Planet not found')
        db.delete(p); db.commit()
    return {'status':'Success'}

@router.post('/compare')
async def compare(req:CompareRequest):
    rows=[]
    for name in req.targets:
        r=await search_target_async(name)
        if r.get('status')=='Success':
            d=r['data']; rows.append({'name':d.get('pl_name',name),'radius_earth':d.get('pl_rade'),'mass_earth':d.get('pl_masse'),'period_days':d.get('pl_orbper'),'temperature_k':d.get('pl_eqt'),'stellar_flux':d.get('pl_insol'),'source':r.get('source')})
        else: rows.append({'name':name,'status':r.get('status'),'message':r.get('message')})
    return {'status':'Success','data':rows}

@router.post('/users/{user_id}/saved-targets')
async def add_saved(user_id:str,req:SaveTargetRequest,request:Request):
    u=require_user(request)
    if u['sub']!=user_id: raise HTTPException(403,'Cannot modify another user')
    return {'status':'Success','id':await asyncio.to_thread(save_target,user_id,req.target_name,req.planet_id)}
@router.get('/users/{user_id}/saved-targets')
async def get_saved(user_id:str,request:Request):
    u=require_user(request)
    if u['sub']!=user_id: raise HTTPException(403,'Forbidden')
    return {'status':'Success','data':await asyncio.to_thread(saved_targets,user_id)}
@router.delete('/users/{user_id}/saved-targets/{saved_id}')
async def remove_saved(user_id:str,saved_id:int,request:Request):
    u=require_user(request)
    if u['sub']!=user_id: raise HTTPException(403,'Forbidden')
    ok=await asyncio.to_thread(delete_saved_target,user_id,saved_id)
    if not ok: raise HTTPException(404,'Saved target not found')
    return {'status':'Success'}

@router.get('/users/{user_id}/activity')
async def activity(user_id:str,request:Request):
    u=require_user(request)
    if u['sub']!=user_id and u['role']!='admin': raise HTTPException(403,'Forbidden')
    return {'status':'Success','data':await asyncio.to_thread(user_activity,user_id)}
@router.post('/comments')
async def add_comment(req:CommentRequest,request:Request):
    u=require_user(request); return {'status':'Success','data':await asyncio.to_thread(add_comment,u['sub'],req.target_name,req.body)}
@router.get('/comments/{target_name:path}')
async def get_comments(target_name:str): return {'status':'Success','data':await asyncio.to_thread(comments,target_name)}
@router.post('/alerts')
async def add_alert(req:AlertRequest,request:Request):
    u=require_user(request); return {'status':'Success','id':await asyncio.to_thread(create_alert,u['sub'],req.target_name,req.alert_type)}
@router.get('/users/{user_id}/alerts')
async def alerts(user_id:str,request:Request):
    u=require_user(request)
    if u['sub']!=user_id: raise HTTPException(403,'Forbidden')
    return {'status':'Success','data':await asyncio.to_thread(user_alerts,user_id)}
@router.get('/active-learning/queue')
async def al_queue(request:Request): require_role(request,'researcher','admin'); return {'status':'Success','data':await asyncio.to_thread(active_learning_queue)}
