import numpy as np
from sklearn.ensemble import IsolationForest
from app.db.repository import list_planets

class CandidateAnomalyDetector:
    _model=None; _size=0
    def _matrix(self):
        rows=list_planets(limit=1000,offset=0); X=[]
        for r in rows:
            vals=[r.get('pl_rade'),r.get('pl_orbper')]
            if all(v is not None for v in vals): X.append(vals)
        return np.asarray(X,float)
    def score(self,target):
        vals=[target.get('pl_rade'),target.get('pl_orbper')]
        X=self._matrix()
        if len(X)<20 or not all(v is not None for v in vals): return {'status':'unavailable','reason':'Reference snapshot does not yet contain >=20 complete radius/period vectors','method':'IsolationForest'}
        if self._model is None or self._size!=len(X): self._model=IsolationForest(n_estimators=250,contamination='auto',random_state=42).fit(X); self._size=len(X)
        pred=int(self._model.predict([vals])[0]); raw=float(self._model.decision_function([vals])[0]); return {'status':'Success','method':'IsolationForest','reference_rows':len(X),'prediction':'anomalous' if pred<0 else 'in_distribution','decision_score':raw}
