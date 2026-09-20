def explain(model,X):
    try:
        import shap
        return {'status':'Success','backend':'SHAP','values':shap.TreeExplainer(model).shap_values(X)}
    except Exception as exc:return {'status':'unavailable','message':str(exc)}
