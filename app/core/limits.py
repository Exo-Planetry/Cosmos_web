from collections import defaultdict, deque
from time import monotonic
from fastapi import HTTPException, Request
from app.core.config import RATE_LIMIT_PER_MINUTE
_hits = defaultdict(deque)

def check_rate_limit(request: Request):
    key = request.client.host if request.client else "unknown"
    now = monotonic(); q = _hits[key]
    while q and now - q[0] > 60: q.popleft()
    if len(q) >= RATE_LIMIT_PER_MINUTE: raise HTTPException(status_code=429, detail="Rate limit exceeded")
    q.append(now)
