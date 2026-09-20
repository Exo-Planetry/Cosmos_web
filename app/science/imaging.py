import numpy as np
def analyze_imaging(values):
    x=np.asarray(values,float)
    if x.size<5:return {'status':'InsufficientData','candidate_support':0.0}
    bg=np.median(x); noise=np.std(x); peak=float(np.max(x)); snr=float((peak-bg)/(noise+1e-12)); return {'status':'Success','method':'background std SNR baseline','candidate_support':float(np.clip(snr/8,0,1)),'snr':snr,'background_median':float(bg),'noise_std':float(noise),'data_status':'Simulated/user supplied','next_steps':['ADI/RDI PSF subtraction','speckle noise model']}
