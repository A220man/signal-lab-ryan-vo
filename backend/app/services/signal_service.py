from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import numpy as np
from app.models.signal import Signal, AnalysisResult, AuditLog, SignalType
from app.models.schemas import SignalGenerateRequest, AnalysisRequest
from app.services.signal_processor import SignalProcessor
from datetime import datetime


class SignalService:
    def __init__(self, db: Session):
        self.db = db

    def generate_signal(self, request: SignalGenerateRequest, user_id: Optional[str] = None) -> Signal:
        data = SignalProcessor.generate_signal(
            signal_type=request.signal_type.value,
            sample_rate=request.sample_rate,
            duration=request.duration,
            frequency=request.frequency,
            amplitude=request.amplitude,
            parameters=request.parameters,
        )

        signal = Signal(
            name=request.name,
            signal_type=request.signal_type,
            sample_rate=request.sample_rate,
            duration=request.duration,
            frequency=request.frequency,
            amplitude=request.amplitude,
            parameters=request.parameters,
            data=data.tolist(),
        )
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)

        self._log_audit(user_id, "create", "signal", str(signal.id), f"Generated {request.signal_type.value} signal")

        return signal

    def get_signal(self, signal_id: int) -> Optional[Signal]:
        return self.db.query(Signal).filter(Signal.id == signal_id).first()

    def list_signals(
        self, skip: int = 0, limit: int = 50, signal_type: Optional[SignalType] = None
    ) -> List[Signal]:
        query = self.db.query(Signal)
        if signal_type:
            query = query.filter(Signal.signal_type == signal_type)
        return query.order_by(Signal.created_at.desc()).offset(skip).limit(limit).all()

    def delete_signal(self, signal_id: int, user_id: Optional[str] = None) -> bool:
        signal = self.get_signal(signal_id)
        if not signal:
            return False
        self.db.delete(signal)
        self.db.commit()
        self._log_audit(user_id, "delete", "signal", str(signal_id))
        return True

    def analyze_signal(self, request: AnalysisRequest, user_id: Optional[str] = None) -> AnalysisResult:
        signal = self.get_signal(request.signal_id)
        if not signal:
            raise ValueError(f"Signal {request.signal_id} not found")

        data = signal.data

        if request.analysis_type == "fft":
            result = SignalProcessor.compute_fft(data, signal.sample_rate)
        elif request.analysis_type == "spectrogram":
            params = request.parameters or {}
            result = SignalProcessor.compute_spectrogram(
                data,
                signal.sample_rate,
                nperseg=params.get("nperseg", 256),
                noverlap=params.get("noverlap"),
                window=params.get("window", "hann"),
            )
        elif request.analysis_type == "statistics":
            result = SignalProcessor.compute_statistics(data)
        else:
            raise ValueError(f"Unknown analysis type: {request.analysis_type}")

        analysis = AnalysisResult(
            signal_id=request.signal_id,
            analysis_type=request.analysis_type,
            result_data=result,
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        self._log_audit(user_id, "analyze", "signal", str(request.signal_id), f"Analysis: {request.analysis_type}")

        return analysis

    def get_analysis(self, analysis_id: int) -> Optional[AnalysisResult]:
        return self.db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()

    def list_analyses(self, signal_id: int) -> List[AnalysisResult]:
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.signal_id == signal_id)
            .order_by(AnalysisResult.created_at.desc())
            .all()
        )

    def export_signal(self, signal_id: int, format: str, include_analysis: bool = False) -> Dict[str, Any]:
        signal = self.get_signal(signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")

        export_data = {
            "id": signal.id,
            "name": signal.name,
            "signal_type": signal.signal_type.value,
            "sample_rate": signal.sample_rate,
            "duration": signal.duration,
            "frequency": signal.frequency,
            "amplitude": signal.amplitude,
            "parameters": signal.parameters,
            "data": signal.data,
            "created_at": signal.created_at.isoformat(),
        }

        if include_analysis:
            analyses = self.list_analyses(signal_id)
            export_data["analyses"] = [
                {
                    "id": a.id,
                    "analysis_type": a.analysis_type,
                    "result_data": a.result_data,
                    "created_at": a.created_at.isoformat(),
                }
                for a in analyses
            ]

        return export_data

    def _log_audit(
        self, user_id: Optional[str], action: str, resource_type: str, resource_id: Optional[str], details: Optional[str] = None
    ):
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
        self.db.add(audit)
        self.db.commit()