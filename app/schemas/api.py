from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default='Researcher', min_length=1, max_length=120)
    role: str = 'researcher'
    @field_validator('email')
    @classmethod
    def clean_email(cls,v): return v.strip().lower()

class AnalysisRequest(BaseModel):
    target: Optional[str]=None
    user_id: Optional[str]=None
    data: Optional[Dict[str,Any]]=None
    time: Optional[List[float]]=None
    light_curve: Optional[List[float]]=None
    rv: Optional[List[float]]=None
    rv_time: Optional[List[float]]=None
    imaging: Optional[List[float]]=None
    atmosphere: Optional[Dict[str,float]]=None
    spectrum: Optional[List[float]]=None

class AtmosphereRequest(BaseModel): composition: Dict[str,float]=Field(default_factory=dict)
class SimulationRequest(BaseModel): values: List[float]=Field(default_factory=list)
class SaveTargetRequest(BaseModel): target_name: str; planet_id: Optional[int]=None
class CompareRequest(BaseModel): targets: List[str]=Field(min_length=2,max_length=6)
class CommentRequest(BaseModel): target_name: str; body: str=Field(min_length=1,max_length=5000)
class AlertRequest(BaseModel): target_name: str; alert_type: str='update'
class WorkspaceRequest(BaseModel): name: str=Field(min_length=1,max_length=160)
