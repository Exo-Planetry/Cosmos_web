import math
def similarity(d):
    parts={}
    if d.get('pl_rade') is not None: parts['radius']=max(0,1-abs(float(d['pl_rade'])-1)/3)
    if d.get('pl_masse') is not None: parts['mass']=max(0,1-abs(float(d['pl_masse'])-1)/10)
    if d.get('pl_eqt') is not None: parts['temperature']=max(0,1-abs(float(d['pl_eqt'])-288)/180)
    if d.get('pl_insol') is not None: parts['stellar_flux']=max(0,1-abs(float(d['pl_insol'])-1)/2)
    score=sum(parts.values())/len(parts) if parts else 0
    return {'score':round(score,3),'components':{k:round(v,3) for k,v in parts.items()},'data_status':'Derived'}
