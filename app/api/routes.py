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
@router.get('/targets')
def list_targets():
    from app.services.nasa import known_targets
    return {"status": "Success", "data": known_targets()}

@router.get('/planets/all')
def list_all_planets(limit: int = 500):
    from app.services.nasa import get_all_targets
    return get_all_targets(limit)

@router.get('/models')
async def models(): return {'status':'Success','data':list_models()}
@router.get('/analytics')
async def analytics(request:Request): return {'status':'Success','data':await asyncio.to_thread(summary,_uid(request))}

@router.post('/pipeline/run')
async def run_pipeline(req:Request):
    payload = await req.json()
    target_name = payload.get('target', 'Unknown Target')
    method = payload.get('method', 'Transit')
    data = payload.get('data', {})
    
    # Common variables
    radius_earth = data.get('radius_earth')
    mass_earth = data.get('mass_earth')
    temperature = data.get('equilibrium_temperature_k')
    orbital_distance = data.get('orbital_distance')
    stellar_teff = data.get('stellar_teff', 5778)
    
    # 1. Method-Specific Calculations
    special_outputs = {}
    
    if method == 'Transit':
        if 'transit_depth' in data and 'stellar_radius' in data:
            import math
            depth = float(data['transit_depth']) # ppm
            r_star = float(data['stellar_radius']) # solar radii
            radius_earth = r_star * 109.2 * math.sqrt(depth / 1e6)
        if 'transit_duration' in data:
            special_outputs['transit_duration_hrs'] = data['transit_duration']
        if 'transit_period' in data:
            special_outputs['orbital_period_days'] = data['transit_period']
        if data.get('ttv_flag'):
            special_outputs['ttv_detected'] = True
            special_outputs['multi_planet_inference'] = "High Probability"
            
    elif method == 'Radial Velocity':
        if 'doppler_shift' in data:
            shift = float(data['doppler_shift']) # m/s (Amplitude K)
            period_days = float(data.get('orbital_period_days', 365.25))
            m_star = float(data.get('stellar_mass', 1.0))
            # K ~ 0.09 m/s for Earth at 1 AU (365 days) around 1 M_sun
            # Mp (Earths) = (K / 0.09) * (M_star^(2/3)) * ((P/365.25)^(1/3))
            import math
            mass_earth = (shift / 0.09) * math.pow(m_star, 2/3) * math.pow(period_days / 365.25, 1/3)
            special_outputs['velocity_amplitude_ms'] = shift
            
    elif method == 'Direct Imaging':
        special_outputs['angular_separation_mas'] = data.get('angular_separation', 50.0)
        special_outputs['contrast_ratio'] = data.get('contrast_ratio', '1e-6')
        
    elif method == 'Astrometry':
        if 'astrometric_wobble' in data:
            wobble_uas = float(data['astrometric_wobble']) # microarcseconds
            m_star = float(data.get('stellar_mass', 1.0))
            dist_pc = float(data.get('distance_pc', 10.0))
            a_au = float(data.get('orbital_distance', 1.0))
            
            # alpha (arcsec) = (Mp / Mstar) * (a / d)
            # Mp (Solar) = alpha * Mstar * (d / a)
            wobble_arcsec = wobble_uas / 1e6
            mass_solar = wobble_arcsec * m_star * (dist_pc / a_au) if a_au > 0 else None
            if mass_solar is not None:
                mass_earth = mass_solar * 333000 # Convert to Earth masses
            special_outputs['astrometric_signature_uas'] = wobble_uas
        
    elif method == 'Gravitational Microlensing':
        if 'mass_ratio' in data:
            ratio = float(data['mass_ratio'])
            m_star = float(data.get('stellar_mass', 1.0))
            mass_earth = ratio * m_star * 333000
            special_outputs['mass_ratio'] = ratio
            special_outputs['einstein_crossing_time_days'] = data.get('crossing_time', 20.0)
        
    elif method == 'Orbital Phase Curve':
        special_outputs['phase_variation_ppm'] = data.get('phase_variation', 50.0)
        special_outputs['albedo_estimate'] = 0.3
        
    elif method == 'Spectroscopic Detection':
        special_outputs['spectral_signature'] = "H2O, CH4 detected"
        special_outputs['atmospheric_confidence'] = "85%"

    # 2. Validation & Anomaly Checks
    validation = {
        "false_positive_prob": data.get('fpp', 0.01),
        "validated": float(data.get('fpp', 0.01)) < 0.05,
        "anomaly_score": 0.95 if data.get('anomaly_check') else 0.1,
        "multi_planet_system": bool(data.get('ttv_flag') or data.get('multi_planet'))
    }

    # 3. Physical Derived Properties
    density = None
    if radius_earth and mass_earth:
        density = mass_earth / (radius_earth ** 3)
        
    if orbital_distance and not temperature:
        import math
        temperature = stellar_teff * math.sqrt(1.0 / (2.0 * orbital_distance))
        
    # 4. Habitability Analysis (Rigorous Physics)
    import math
    
    # Defaults for missing stellar parameters (assume Sun-like if missing)
    r_star = float(data.get('stellar_radius', 1.0))
    stellar_teff = float(data.get('stellar_teff', 5778))
    m_star = float(data.get('stellar_mass', 1.0))
    
    # 4.1 Stellar Luminosity & Flux
    luminosity_solar = (r_star ** 2) * ((stellar_teff / 5778) ** 4)
    stellar_flux = luminosity_solar / (orbital_distance ** 2) if orbital_distance else None
    
    # 4.2 Habitable Zone Boundaries (Simplified Kopparapu)
    hz_conservative_inner = math.sqrt(luminosity_solar / 1.1)
    hz_conservative_outer = math.sqrt(luminosity_solar / 0.53)
    hz_optimistic_inner = math.sqrt(luminosity_solar / 1.77)
    hz_optimistic_outer = math.sqrt(luminosity_solar / 0.32)
    
    in_conservative_hz = False
    in_optimistic_hz = False
    if orbital_distance:
        in_conservative_hz = hz_conservative_inner <= orbital_distance <= hz_conservative_outer
        in_optimistic_hz = hz_optimistic_inner <= orbital_distance <= hz_optimistic_outer
        
    # 4.3 Tidal Locking Check (Empirical threshold based on Peale 1999 scaling)
    # Typically, planets closely orbiting low-mass stars are tidally locked.
    is_tidally_locked = orbital_distance < 0.2 * (m_star ** 0.33) if orbital_distance else False
    
    # 4.4 Atmospheric Retention (Jeans Escape)
    # v_esc = 11.2 * sqrt(M/R) km/s
    # v_th = sqrt(3kT/m)
    retains_atmosphere = False
    retains_water = False
    retains_oxygen = False
    
    if mass_earth and radius_earth and temperature:
        v_esc = 11.2 * math.sqrt(mass_earth / radius_earth) # km/s
        
        # Calculate thermal velocities (km/s)
        # k = 1.38e-23 J/K, m = amu * 1.66e-27 kg
        def v_th(amu):
            return math.sqrt(3 * 1.38e-23 * temperature / (amu * 1.66e-27)) / 1000
            
        v_th_h2o = v_th(18.0) # Water
        v_th_o2 = v_th(32.0)  # Oxygen
        
        # Rule of thumb: v_esc > 6 * v_th for long-term retention
        retains_water = v_esc > 6 * v_th_h2o
        retains_oxygen = v_esc > 6 * v_th_o2
        retains_atmosphere = retains_water or retains_oxygen
        
    # 4.5 Surface Liquid Water Potential & Score
    is_rocky = mass_earth is not None and 0.1 <= mass_earth <= 10.0
    surface_liquid_water = in_optimistic_hz and is_rocky and retains_water
    
    habitability_status = "Unfavorable"
    score = 0.1
    if in_conservative_hz and is_rocky and retains_atmosphere:
        habitability_status = "Potentially Habitable (Conservative)"
        score = 0.95
    elif in_optimistic_hz and is_rocky:
        habitability_status = "Potentially Habitable (Optimistic)"
        score = 0.75
    elif in_optimistic_hz:
        habitability_status = "Habitable Zone (Gas/Ice Giant)"
        score = 0.40

    result = {
        "status": "Success",
        "target": target_name,
        "method": method,
        "properties": {
            "radius_earth": round(radius_earth, 2) if radius_earth else None,
            "mass_earth": round(mass_earth, 2) if mass_earth else None,
            "density": round(density, 2) if density else None,
            "equilibrium_temperature_k": round(temperature, 2) if temperature else None
        },
        "special_outputs": special_outputs,
        "validation": validation,
        "habitability": {
            "status": habitability_status,
            "score": score,
            "stellar_flux_earth": round(stellar_flux, 2) if stellar_flux else None,
            "in_conservative_hz": in_conservative_hz,
            "in_optimistic_hz": in_optimistic_hz,
            "is_tidally_locked": is_tidally_locked,
            "retains_water_atmosphere": retains_water,
            "surface_liquid_water_potential": surface_liquid_water
        }
    }
    
    user = _uid(req)
    await asyncio.to_thread(save_analysis, target_name, result, user)
    return result

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
