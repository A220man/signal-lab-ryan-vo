from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas import (
    SignalGenerateRequest,
    SignalGenerateResponse,
    SignalListResponse,
    AnalysisRequest,
    AnalysisResponse,
    ExportRequest,
)
from app.services.signal_service import SignalService
from app.models.signal import SignalType

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.post("/generate", response_model=SignalGenerateResponse)
def generate_signal(request: SignalGenerateRequest, db: Session = Depends(get_db)):
    service = SignalService(db)
    try:
        signal = service.generate_signal(request, user_id="anonymous")
        return SignalGenerateResponse(
            id=signal.id,
            name=signal.name,
            signal_type=signal.signal_type,
            sample_rate=signal.sample_rate,
            duration=signal.duration,
            frequency=signal.frequency,
            amplitude=signal.amplitude,
            parameters=signal.parameters,
            data=signal.data,
            created_at=signal.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[SignalListResponse])
def list_signals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    signal_type: Optional[SignalType] = None,
    db: Session = Depends(get_db),
):
    service = SignalService(db)
    signals = service.list_signals(skip=skip, limit=limit, signal_type=signal_type)
    return [
        SignalListResponse(
            id=s.id,
            name=s.name,
            signal_type=s.signal_type,
            sample_rate=s.sample_rate,
            duration=s.duration,
            frequency=s.frequency,
            amplitude=s.amplitude,
            created_at=s.created_at,
        )
        for s in signals
    ]


@router.get("/{signal_id}", response_model=SignalGenerateResponse)
def get_signal(signal_id: int, db: Session = Depends(get_db)):
    service = SignalService(db)
    signal = service.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return SignalGenerateResponse(
        id=signal.id,
        name=signal.name,
        signal_type=signal.signal_type,
        sample_rate=signal.sample_rate,
        duration=signal.duration,
        frequency=signal.frequency,
        amplitude=signal.amplitude,
        parameters=signal.parameters,
        data=signal.data,
        created_at=signal.created_at,
    )


@router.delete("/{signal_id}")
def delete_signal(signal_id: int, db: Session = Depends(get_db)):
    service = SignalService(db)
    if not service.delete_signal(signal_id, user_id="anonymous"):
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"message": "Signal deleted"}


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_signal(request: AnalysisRequest, db: Session = Depends(get_db)):
    service = SignalService(db)
    try:
        analysis = service.analyze_signal(request, user_id="anonymous")
        return AnalysisResponse(
            id=analysis.id,
            signal_id=analysis.signal_id,
            analysis_type=analysis.analysis_type,
            result_data=analysis.result_data,
            created_at=analysis.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{signal_id}/analyses", response_model=List[AnalysisResponse])
def list_analyses(signal_id: int, db: Session = Depends(get_db)):
    service = SignalService(db)
    analyses = service.list_analyses(signal_id)
    return [
        AnalysisResponse(
            id=a.id,
            signal_id=a.signal_id,
            analysis_type=a.analysis_type,
            result_data=a.result_data,
            created_at=a.created_at,
        )
        for a in analyses
    ]


@router.get("/{signal_id}/export")
def export_signal(
    signal_id: int,
    format: str = Query("json", pattern="^(json|csv|wav)$"),
    include_analysis: bool = False,
    db: Session = Depends(get_db),
):
    service = SignalService(db)
    try:
        export_data = service.export_signal(signal_id, format, include_analysis)
        return export_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))