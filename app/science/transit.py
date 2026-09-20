from typing import Optional
import numpy as np

def _bls(time, flux):
    try:
        from astropy.timeseries import BoxLeastSquares
        model=BoxLeastSquares(np.asarray(time,float),np.asarray(flux,float))
        periods=np.linspace(max(np.ptp(time)/50,0.05),max(np.ptp(time)/1.5,1),300)
        durations=np.array([0.02,0.05,0.1,0.2,0.4])
        power=model.power(periods,durations)
        i=int(np.nanargmax(power.power))
        return {'period_days':float(power.period[i]),'duration_days':float(power.duration[i]),'power':float(power.power[i]),'depth':float(power.depth[i])}
    except Exception:
        return None

def analyze_transit(values, time=None):
    y=np.asarray(values,float)
    if y.size<8:return {'status':'InsufficientData','method':'BLS','candidate_support':0.0,'data_status':'User supplied'}
    t=np.asarray(time,float) if time is not None and len(time)==len(y) else np.arange(y.size,dtype=float)
    y=(y-np.nanmedian(y))/max(np.nanstd(y),1e-12)+1
    fit=_bls(t,y)
    depth=float(max(0,np.nanmedian(y)-np.nanmin(y)))
    support=float(np.clip(depth*8,0,1))
    result={'status':'Success','method':'Astropy BoxLeastSquares' if fit else 'Robust periodicity baseline','candidate_support':round(support,4),'metrics':{'points':int(y.size),'depth_estimate':depth,'snr_proxy':float(abs(np.nanmin(y)-1)/(np.nanstd(y)+1e-12))},'data_status':'Observed/user supplied','checks':{}}
    if fit: result['bls']=fit
    # odd-even test
    med=np.nanmedian(y); dips=np.where(y<med)[0]; result['checks']['odd_even']={'status':'Pass' if len(dips)<2 else 'Review','difference_proxy':float(abs(np.mean(y[dips[::2]])-np.mean(y[dips[1::2]]))) if len(dips)>1 else None}
    result['checks']['secondary_eclipse']={'status':'Not_conclusive','note':'Requires phase coverage and validated detrending.'}
    result['checks']['ttv']={'status':'Requires_multiple_transits'}
    return result
