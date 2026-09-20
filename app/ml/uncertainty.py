import numpy as np
def bootstrap_mean(values,n=1000,seed=42):
    x=np.asarray(values,float); x=x[np.isfinite(x)]
    if not len(x):return {'status':'InsufficientData'}
    rng=np.random.default_rng(seed); means=rng.choice(x,(n,len(x)),replace=True).mean(axis=1); return {'status':'Success','mean':float(x.mean()),'std':float(x.std(ddof=1)) if len(x)>1 else 0,'ci95':[float(np.quantile(means,.025)),float(np.quantile(means,.975))],'method':'bootstrap'}
