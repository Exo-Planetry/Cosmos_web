def assess_habitability(d):
    flux=d.get('pl_insol') or d.get('stellar_flux'); temp=d.get('pl_eqt') or d.get('equilibrium_temp_k'); score=0
    if flux is not None: score+=0.55 if 0.25<=float(flux)<=1.8 else 0
    if temp is not None: score+=0.45 if 180<=float(temp)<=320 else 0
    return {'score':round(score,3),'classification':'favorable HZ context' if score>=.7 else 'partial HZ context' if score>=.4 else 'limited HZ context','warning':'Habitable-zone location does not establish surface habitability.','inputs':{'stellar_flux':flux,'equilibrium_temp_k':temp},'data_status':'Derived from available catalog parameters'}
