def explain_tabular(features,score):
    refs={'pl_rade':1,'pl_masse':1,'pl_eqt':288,'pl_insol':1,'pl_orbper':10}
    out=[]
    for k,ref in refs.items():
        v=features.get(k)
        if v is None:continue
        delta=abs(float(v)-ref)/(abs(ref)+1e-9); direction='supports' if delta<.75 else 'deviates'
        out.append({'feature':k,'value':v,'reference':ref,'effect':direction,'magnitude':round(min(delta,2),3)})
    return {'status':'interpretable_baseline','global_score':score,'features':out,'note':'SHAP is enabled when the optional shap dependency and trained model artifact are available.'}
