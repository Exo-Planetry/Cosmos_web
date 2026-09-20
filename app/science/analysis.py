import uuid
from datetime import datetime,timezone
import numpy as np
from app.services.nasa import search_target
from app.science.transit import analyze_transit
from app.science.orbit import keplerian_rv, planet_physics
from app.science.imaging import analyze_imaging
from app.science.atmosphere import analyze_atmosphere, spectral_anomaly
from app.science.habitability import assess_habitability
from app.science.physics import similarity
from app.science.lensing import einstein_angle

def _num(v):
    try:return float(v) if v not in (None,'') else None
    except:return None

def analyze(target_name,payload):
    target=payload.get('data') if isinstance(payload.get('data'),dict) else None; source='User supplied'
    if not target:
        lookup=search_target(target_name)
        if lookup.get('status')=='Success':target=lookup['data'];source=lookup.get('source','NASA')
        else:
            target={k:payload.get(k) for k in ['pl_orbper','pl_rade','pl_masse','pl_eqt','pl_insol','pl_orbeccen','pl_orbincl','pl_trandep','pl_trandur','pl_orbsmax','st_lum','st_teff','st_mass'] if payload.get(k) is not None};source=lookup.get('source','User supplied')
            if not target and not any(payload.get(k) for k in ('light_curve','rv','imaging','atmosphere','spectrum')):raise ValueError(lookup.get('message','Target data unavailable'))
    modules={}; evidence={}
    if payload.get('light_curve'):
        modules['transit']=analyze_transit(payload['light_curve'],payload.get('time'));evidence['transit']=modules['transit']['candidate_support']
    elif target.get('pl_trandep') is not None:
        depth=float(target['pl_trandep']);support=float(np.clip(depth/0.01,0,1));modules['transit']={'status':'Success','method':'Catalog transit evidence','candidate_support':support,'metrics':{'catalog_depth_fraction':depth,'catalog_depth_ppm':depth*1e6},'data_status':'Catalogued; not a new detection'};evidence['transit']=support
    if payload.get('rv'):
        modules['radial_velocity']=keplerian_rv(payload.get('rv_time') or list(range(len(payload['rv']))),payload['rv'],_num(target.get('st_mass')) or 1);evidence['radial_velocity']=modules['radial_velocity']['candidate_support']
    if payload.get('imaging'):modules['direct_imaging']=analyze_imaging(payload['imaging']);evidence['direct_imaging']=modules['direct_imaging']['candidate_support']
    if payload.get('atmosphere'):modules['atmosphere']=analyze_atmosphere(payload['atmosphere']);evidence['atmosphere']=modules['atmosphere']['potential_biosignature_evidence']
    if payload.get('spectrum'):modules['spectral_anomaly']=spectral_anomaly(payload['spectrum']);evidence['spectral_anomaly']=modules['spectral_anomaly']['candidate_support']
    modules['planet_physics']=planet_physics(_num(target.get('pl_rade')),_num(target.get('pl_masse')),_num(target.get('pl_orbper')),_num(target.get('st_mass')) or 1);modules['habitability']=assess_habitability(target);modules['similarity']=similarity(target)
    if modules['planet_physics'].get('density_g_cm3') is not None:evidence['physical_consistency']=float(np.clip(1-abs(modules['planet_physics']['density_g_cm3']-5.51)/12,0,1))
    if not evidence:evidence['data_quality']=0.35
    score=float(np.mean(list(evidence.values())))
    fp=max(0,min(1,1-score))
    label='Strong candidate evidence' if score>=.8 else 'Promising candidate — validation required' if score>=.6 else 'Possible candidate — more evidence needed' if score>=.4 else 'Insufficient evidence'
    return {'status':'Success','version':'5.0.0','target_name':target.get('pl_name',target_name),'target_data':target,'data_source':source,'candidate_assessment':{'score':round(score*100,1),'label':label,'false_positive_risk':round(fp*100,1),'uncertainty':round(max(.02,1-score),4),'not_confirmation':True},'evidence_fusion':{k:round(v,4) for k,v in evidence.items()},'modules':modules,'provenance':{'analysis_id':uuid.uuid4().hex,'pipeline_version':'COSMOS-5.0','model_status':'research baselines; no fabricated training metrics','timestamp_utc':datetime.now(timezone.utc).isoformat(),'data_status':'Observed/catalogued/derived/simulated status retained per module'},'research_mode':{'enabled':False,'artifacts':['raw inputs','processed series','fit parameters','residuals','model explanation','provenance']}}
