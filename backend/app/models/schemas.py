from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum
import numpy as np


class SignalType(str, Enum):
    SINE = "sine"
    SQUARE = "square"
    NOISE = "noise"
    CHIRP = "chirp"


class SignalGenerateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    signal_type: SignalType
    sample_rate: int = Field(..., gt=0, le=192000)
    duration: float = Field(..., gt=0, le=3600)
    frequency: Optional[float] = Field(None, gt=0)
    amplitude: float = Field(1.0, gt=0, le=10)
    parameters: Optional[Dict[str, Any]] = None


class SignalGenerateResponse(BaseModel):
    id: int
    name: str
    signal_type: SignalType
    sample_rate: int
    duration: float
    frequency: Optional[float]
    amplitude: float
    parameters: Optional[Dict[str, Any]]
    data: List[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignalListResponse(BaseModel):
    id: int
    name: str
    signal_type: SignalType
    sample_rate: int
    duration: float
    frequency: Optional[float]
    amplitude: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisRequest(BaseModel):
    signal_id: int
    analysis_type: str = Field(..., pattern="^(fft|spectrogram|statistics)$")
    parameters: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    id: int
    signal_id: int
    analysis_type: str
    result_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExportRequest(BaseModel):
    format: str = Field("json", pattern="^(json|csv|wav)$")
    include_analysis: bool = False