import math
G=6.67430e-11;c=299792458.;MSUN=1.98847e30;PC=3.085677581e16
def einstein_angle(mass_solar,lens_distance_pc,source_distance_pc):
    Dl=lens_distance_pc*PC; Ds=source_distance_pc*PC; Dls=max(Ds-Dl,0); theta=math.sqrt(4*G*(mass_solar*MSUN)/c**2*Dls/(Dl*Ds)) if Dls>0 else 0
    return {'status':'Success','method':'Einstein angle geometry','einstein_angle_mas':theta*206265000,'data_status':'Derived','note':'Geometry only; microlensing detection requires a time-series fit.'}

def paczynski(time, baseline=1.0, u0=0.2, t0=0.0, tE=10.0, blend=0.0):
    import numpy as np
    t=np.asarray(time,float); u=np.sqrt(u0**2+((t-t0)/tE)**2); A=(u**2+2)/(u*np.sqrt(u**2+4)); return baseline*(1-blend)+baseline*blend*A
