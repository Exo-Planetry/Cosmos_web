def uncertainty_priority(prediction,model_uncertainty):
    p=float(prediction); u=float(model_uncertainty); return {'priority':round(u*(1-abs(p-.5)*2),4),'prediction':p,'uncertainty':u,'strategy':'review uncertain candidates first'}
