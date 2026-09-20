import numpy as np
MOLECULES={'H2O':1.0,'CO2':0.8,'CH4':0.7,'O2':0.7,'O3':0.9,'CO':0.4,'NH3':0.4,'SO2':0.5}
def analyze_atmosphere(composition):
    c={str(k).upper():float(v) for k,v in composition.items()}; present=[k for k,v in c.items() if v>0.01]; bio=float(np.clip((c.get('O2',0)*0.25+c.get('O3',0)*0.25+c.get('CH4',0)*0.2+c.get('H2O',0)*0.1),0,1))
    return {'status':'Success','method':'molecular composition assessment','molecules_detected':present,'potential_biosignature_evidence':bio,'false_positive_context':['Abiotic O2/O3 pathways','Photochemistry','Stellar activity'],'data_status':'User supplied/simulated','warning':'Potential atmospheric indicators are not evidence of life.'}
def spectral_anomaly(values):
    x=np.asarray(values,float)
    if x.size<6:return {'status':'InsufficientData','candidate_support':0.0}
    z=np.abs((x-np.median(x))/(np.std(x)+1e-12)); score=float(np.clip(np.mean(z>3)*2,0,1)); return {'status':'Success','method':'robust spectral anomaly baseline','candidate_support':score,'anomalous_fraction':float(np.mean(z>3)),'data_status':'User supplied'}
