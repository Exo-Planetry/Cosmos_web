import json, uuid
from sqlalchemy import func, select, delete
from app.db.database import SessionLocal, init_db
from app.db.models import User, Planet, Observation, AnalysisRun, ModelRun, SavedTarget, ActivityLog, Alert, Comment, Workspace, ActiveLearningItem

def _f(v):
    try: return float(v) if v not in (None,'') else None
    except: return None

def ensure_user(email, password_hash, display_name='Researcher', role='researcher', user_id=None):
    init_db()
    with SessionLocal() as db:
        u=db.scalar(select(User).where(User.email==email.lower()))
        if not u:
            u=User(id=user_id or uuid.uuid4().hex,email=email.lower(),password_hash=password_hash,display_name=display_name,role=role); db.add(u); db.commit(); db.refresh(u)
        return u

def user_by_email(email):
    init_db();
    with SessionLocal() as db: return db.scalar(select(User).where(User.email==email.lower()))

def user_by_id(uid):
    init_db();
    with SessionLocal() as db: return db.get(User,uid)

def log_activity(uid,action,detail=''):
    with SessionLocal() as db: db.add(ActivityLog(user_id=uid,action=action,detail=detail)); db.commit()

def upsert_planet(data, source='NASA'):
    init_db(); name=str(data.get('pl_name') or data.get('name') or 'Unknown')
    with SessionLocal() as db:
        p=db.scalar(select(Planet).where(Planet.name==name)) or Planet(name=name)
        p.host_star=data.get('hostname') or data.get('host_star'); p.radius_earth=_f(data.get('pl_rade') or data.get('radius_earth')); p.mass_earth=_f(data.get('pl_masse') or data.get('mass_earth')); p.orbital_period_days=_f(data.get('pl_orbper') or data.get('orbital_period_days')); p.equilibrium_temp_k=_f(data.get('pl_eqt') or data.get('equilibrium_temp_k')); p.stellar_flux=_f(data.get('pl_insol') or data.get('stellar_flux')); p.source=source; p.payload_json=json.dumps(data,default=str); db.add(p); db.commit(); db.refresh(p); return p

def list_planets(query=None,limit=50,offset=0):
    init_db();
    with SessionLocal() as db:
        q=select(Planet).order_by(Planet.name).offset(offset).limit(limit)
        if query: q=select(Planet).where(Planet.name.ilike(f'%{query}%')).order_by(Planet.name).offset(offset).limit(limit)
        return [dict(json.loads(p.payload_json),db_id=p.id,source=p.source) for p in db.scalars(q).all()]

def count_planets(query=None):
    init_db();
    with SessionLocal() as db:
        q=select(func.count(Planet.id));
        if query:q=q.where(Planet.name.ilike(f'%{query}%'))
        return db.scalar(q) or 0

def save_analysis(target_name,result,user_id=None):
    init_db(); aid=result.get('provenance',{}).get('analysis_id') or uuid.uuid4().hex; score=float(result.get('candidate_assessment',{}).get('score',0)); label=result.get('candidate_assessment',{}).get('label','Assessment'); public_token=uuid.uuid4().hex; result.setdefault('provenance',{})['public_token']=public_token
    with SessionLocal() as db:
        db.merge(AnalysisRun(id=aid,user_id=user_id,target_name=target_name,score=score,label=label,public_token=public_token,result_json=json.dumps(result,default=str))); db.commit()
    return aid

def get_analysis(aid):
    init_db();
    with SessionLocal() as db:
        r=db.get(AnalysisRun,aid); return json.loads(r.result_json) if r else None

def recent_analyses(user_id=None,limit=20,offset=0):
    init_db();
    with SessionLocal() as db:
        q=select(AnalysisRun).order_by(AnalysisRun.created_at.desc()).offset(offset).limit(limit)
        if user_id:q=q.where(AnalysisRun.user_id==user_id)
        return [{'id':r.id,'target_name':r.target_name,'score':r.score,'label':r.label,'created_at':r.created_at.isoformat()} for r in db.scalars(q).all()]

def count_analyses(user_id=None):
    init_db();
    with SessionLocal() as db:
        q=select(func.count(AnalysisRun.id));
        if user_id:q=q.where(AnalysisRun.user_id==user_id)
        return db.scalar(q) or 0

def save_observation(target_name,source,observation_type,status='Observed',metadata=None,planet_id=None):
    with SessionLocal() as db:
        r=Observation(target_name=target_name,source=source,observation_type=observation_type,status=status,metadata_json=json.dumps(metadata or {}),planet_id=planet_id); db.add(r); db.commit(); db.refresh(r); return r.id

def save_model_run(aid,name,version,metrics):
    with SessionLocal() as db: db.add(ModelRun(id=uuid.uuid4().hex,analysis_id=aid,model_name=name,model_version=version,metrics_json=json.dumps(metrics))); db.commit()

def save_target(uid,name,planet_id=None):
    init_db();
    with SessionLocal() as db:
        existing=db.scalar(select(SavedTarget).where(SavedTarget.user_id==uid,SavedTarget.target_name==name))
        if existing:return existing.id
        r=SavedTarget(user_id=uid,target_name=name,planet_id=planet_id); db.add(r); db.commit(); db.refresh(r); return r.id

def saved_targets(uid,limit=50,offset=0):
    with SessionLocal() as db:return [{'id':r.id,'target_name':r.target_name,'planet_id':r.planet_id,'created_at':r.created_at.isoformat()} for r in db.scalars(select(SavedTarget).where(SavedTarget.user_id==uid).order_by(SavedTarget.created_at.desc()).offset(offset).limit(limit)).all()]

def delete_saved_target(uid,sid):
    with SessionLocal() as db:r=db.scalar(select(SavedTarget).where(SavedTarget.id==sid,SavedTarget.user_id==uid));
    
    if not r:return False
    with SessionLocal() as db: db.execute(delete(SavedTarget).where(SavedTarget.id==sid,SavedTarget.user_id==uid)); db.commit(); return True

def add_comment(uid,target,body):
    with SessionLocal() as db:r=Comment(user_id=uid,target_name=target,body=body); db.add(r); db.commit(); db.refresh(r); return {'id':r.id,'target_name':r.target_name,'body':r.body,'created_at':r.created_at.isoformat()}

def comments(target):
    with SessionLocal() as db:return [{'id':r.id,'user_id':r.user_id,'target_name':r.target_name,'body':r.body,'created_at':r.created_at.isoformat()} for r in db.scalars(select(Comment).where(Comment.target_name==target).order_by(Comment.created_at.desc())).all()]

def create_alert(uid,target,alert_type='update'):
    with SessionLocal() as db:r=Alert(user_id=uid,target_name=target,alert_type=alert_type); db.add(r); db.commit(); db.refresh(r); return r.id

def user_alerts(uid):
    with SessionLocal() as db:return [{'id':r.id,'target_name':r.target_name,'type':r.alert_type,'enabled':r.enabled} for r in db.scalars(select(Alert).where(Alert.user_id==uid)).all()]

def user_activity(uid,limit=50):
    with SessionLocal() as db:return [{'action':r.action,'detail':r.detail,'created_at':r.created_at.isoformat()} for r in db.scalars(select(ActivityLog).where(ActivityLog.user_id==uid).order_by(ActivityLog.created_at.desc()).limit(limit)).all()]

def set_verification_token(uid, token):
    with SessionLocal() as db:
        u=db.get(User,uid)
        if not u:return False
        u.verification_token=token; db.commit(); return True

def verify_user_token(token):
    with SessionLocal() as db:
        u=db.scalar(select(User).where(User.verification_token==token))
        if not u:return False
        u.is_verified=True; u.verification_token=None; db.commit(); return True

def set_reset_token(email, token):
    with SessionLocal() as db:
        u=db.scalar(select(User).where(User.email==email.lower()))
        if not u:return False
        u.reset_token=token; db.commit(); return True

def reset_password(token,password_hash):
    with SessionLocal() as db:
        u=db.scalar(select(User).where(User.reset_token==token))
        if not u:return False
        u.password_hash=password_hash; u.reset_token=None; db.commit(); return True

def public_analysis(token):
    with SessionLocal() as db:
        r=db.scalar(select(AnalysisRun).where(AnalysisRun.public_token==token)); return json.loads(r.result_json) if r else None

def analysis_csv(aid):
    import csv, io
    result=get_analysis(aid)
    if not result:return None
    out=io.StringIO(); w=csv.writer(out); w.writerow(['field','value'])
    for k,v in result.get('target_data',{}).items():w.writerow([k,v])
    return out.getvalue()

def analysis_trend(target_name,limit=20):
    with SessionLocal() as db:
        rows=db.scalars(select(AnalysisRun).where(AnalysisRun.target_name==target_name).order_by(AnalysisRun.created_at.asc()).limit(limit)).all()
        return [{'id':r.id,'score':r.score,'created_at':r.created_at.isoformat()} for r in rows]

def summary(uid=None):
    total=count_analyses(uid); avg=0
    with SessionLocal() as db:
        q=select(func.avg(AnalysisRun.score));
        if uid:q=q.where(AnalysisRun.user_id==uid)
        avg=float(db.scalar(q) or 0)
        saved=db.scalar(select(func.count(SavedTarget.id)).where(SavedTarget.user_id==uid)) if uid else 0
    return {'total_analyses':total,'average_candidate_score':round(avg,1),'saved_targets':int(saved or 0),'recent':recent_analyses(uid,5,0)}

def queue_active_learning(target,uncertainty,payload,priority=None):
    with SessionLocal() as db:r=ActiveLearningItem(target_name=target,uncertainty=float(uncertainty),priority=float(priority if priority is not None else uncertainty),payload_json=json.dumps(payload)); db.add(r); db.commit(); db.refresh(r); return r.id

def active_learning_queue(limit=100):
    with SessionLocal() as db:return [{'id':r.id,'target_name':r.target_name,'uncertainty':r.uncertainty,'priority':r.priority,'status':r.status,'payload':json.loads(r.payload_json)} for r in db.scalars(select(ActiveLearningItem).order_by(ActiveLearningItem.priority.desc()).limit(limit)).all()]
