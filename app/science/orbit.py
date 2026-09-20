import numpy as np
G=6.67430e-11; AU=1.495978707e11; MSUN=1.98847e30; MEARTH=5.9722e24; REARTH=6.371e6

def planet_physics(radius_earth,mass_earth,period_days,star_mass=1.0):
    r=radius_earth*REARTH if radius_earth else None; m=mass_earth*MEARTH if mass_earth else None
    out={'status':'Derived'}
    if r and m:
        out['density_g_cm3']=float((m/(4/3*np.pi*r**3))/1000); out['surface_gravity_m_s2']=float(G*m/r**2); out['escape_velocity_km_s']=float(np.sqrt(2*G*m/r)/1000)
    if period_days:
        out['semi_major_axis_au']=float(((G*(star_mass*MSUN)*(period_days*86400)**2/(4*np.pi**2))**(1/3))/AU)
    return out

def _kepler(M,e):
    E=M.copy()
    for _ in range(12): E-= (E-e*np.sin(E)-M)/(1-e*np.cos(E))
    return E

def keplerian_rv(time,values,star_mass=1.0):
    t=np.asarray(time,float); y=np.asarray(values,float)
    if y.size<5:return {'status':'InsufficientData','candidate_support':0.0,'method':'Keplerian baseline'}
    centered=y-np.nanmean(y); freqs=np.linspace(1/max(np.ptp(t),1),0.5/max(np.median(np.diff(t)) if len(t)>1 else 1,1e-3),300)
    best=None
    for f in freqs:
        X=np.column_stack([np.sin(2*np.pi*f*t),np.cos(2*np.pi*f*t),np.ones_like(t)])
        coef=np.linalg.lstsq(X,y,rcond=None)[0]; resid=y-X@coef; rss=float(np.mean(resid**2))
        if best is None or rss<best[0]:best=(rss,f,coef,resid)
    rss,f,coef,resid=best; period=1/f; amp=float(np.hypot(coef[0],coef[1])); support=float(np.clip(amp/(np.std(y)+1e-12)*0.35,0,1))
    # minimum mass estimate from K and period, assuming sin(i)=1, circular baseline
    K=amp; mass_mj=K*(period**(1/3))*(star_mass**(2/3))*0.001 if K else None
    return {'status':'Success','method':'Keplerian circular baseline + least squares','candidate_support':round(support,4),'period_days':float(period),'semi_amplitude':K,'systemic_velocity':float(coef[2]),'residual_rms':float(np.sqrt(rss)),'planet_mass_mjup_estimate':mass_mj,'model':'single-planet circular; eccentric/multi-planet Bayesian fit is a research extension'}
