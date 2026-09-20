from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from app.db.database import Base

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__='users'
    id: Mapped[str]=mapped_column(String(64), primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(512))
    display_name: Mapped[str]=mapped_column(String(120), default='Researcher')
    role: Mapped[str]=mapped_column(String(30), default='researcher')
    is_verified: Mapped[bool]=mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]]=mapped_column(String(128), nullable=True)
    reset_token: Mapped[Optional[str]]=mapped_column(String(128), nullable=True)
    totp_secret: Mapped[Optional[str]]=mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Planet(Base):
    __tablename__='planets'
    id: Mapped[int]=mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]=mapped_column(String(180), unique=True, index=True)
    host_star: Mapped[Optional[str]]=mapped_column(String(180), nullable=True)
    radius_earth: Mapped[Optional[float]]=mapped_column(Float)
    mass_earth: Mapped[Optional[float]]=mapped_column(Float)
    orbital_period_days: Mapped[Optional[float]]=mapped_column(Float)
    equilibrium_temp_k: Mapped[Optional[float]]=mapped_column(Float)
    stellar_flux: Mapped[Optional[float]]=mapped_column(Float)
    source: Mapped[str]=mapped_column(String(120), default='NASA')
    payload_json: Mapped[str]=mapped_column(Text, default='{}')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Observation(Base):
    __tablename__='observations'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    planet_id: Mapped[Optional[int]]=mapped_column(ForeignKey('planets.id', ondelete='SET NULL'), nullable=True, index=True)
    target_name: Mapped[str]=mapped_column(String(180), index=True)
    source: Mapped[str]=mapped_column(String(120))
    observation_type: Mapped[str]=mapped_column(String(80))
    status: Mapped[str]=mapped_column(String(80), default='Observed')
    metadata_json: Mapped[str]=mapped_column(Text, default='{}')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class AnalysisRun(Base):
    __tablename__='analysis_runs'
    id: Mapped[str]=mapped_column(String(64), primary_key=True)
    user_id: Mapped[Optional[str]]=mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    target_name: Mapped[str]=mapped_column(String(180), index=True)
    score: Mapped[float]=mapped_column(Float, default=0)
    label: Mapped[str]=mapped_column(String(180), default='Assessment')
    result_json: Mapped[str]=mapped_column(Text, default='{}')
    public_token: Mapped[str]=mapped_column(String(64), unique=True, index=True, default=lambda: uuid.uuid4().hex)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, index=True)

class ModelRun(Base):
    __tablename__='model_runs'
    id: Mapped[str]=mapped_column(String(64), primary_key=True)
    analysis_id: Mapped[str]=mapped_column(ForeignKey('analysis_runs.id', ondelete='CASCADE'), index=True)
    model_name: Mapped[str]=mapped_column(String(120))
    model_version: Mapped[str]=mapped_column(String(80))
    metrics_json: Mapped[str]=mapped_column(Text, default='{}')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class SavedTarget(Base):
    __tablename__='saved_targets'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[str]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    planet_id: Mapped[Optional[int]]=mapped_column(ForeignKey('planets.id', ondelete='SET NULL'), nullable=True)
    target_name: Mapped[str]=mapped_column(String(180), index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    __table_args__=(UniqueConstraint('user_id','target_name',name='uq_saved_target'),)

class ActivityLog(Base):
    __tablename__='activity_logs'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[str]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    action: Mapped[str]=mapped_column(String(120))
    detail: Mapped[str]=mapped_column(Text, default='')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Alert(Base):
    __tablename__='alerts'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[str]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    target_name: Mapped[str]=mapped_column(String(180), index=True)
    alert_type: Mapped[str]=mapped_column(String(80), default='update')
    enabled: Mapped[bool]=mapped_column(Boolean, default=True)
    last_seen_json: Mapped[str]=mapped_column(Text, default='{}')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Comment(Base):
    __tablename__='comments'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[str]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    target_name: Mapped[str]=mapped_column(String(180), index=True)
    body: Mapped[str]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Workspace(Base):
    __tablename__='workspaces'
    id: Mapped[str]=mapped_column(String(64), primary_key=True)
    owner_id: Mapped[str]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    name: Mapped[str]=mapped_column(String(160))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class ActiveLearningItem(Base):
    __tablename__='active_learning_queue'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    target_name: Mapped[str]=mapped_column(String(180), index=True)
    uncertainty: Mapped[float]=mapped_column(Float, default=0)
    priority: Mapped[float]=mapped_column(Float, default=0)
    status: Mapped[str]=mapped_column(String(40), default='queued')
    payload_json: Mapped[str]=mapped_column(Text, default='{}')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
