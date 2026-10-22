import pytest
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.signal import Signal, AnalysisResult, AuditLog, SignalType

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


class TestModels:
    def setup_method(self):
        self.db = TestingSessionLocal()

    def teardown_method(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_create_signal(self):
        signal = Signal(
            name="Test Signal",
            signal_type=SignalType.SINE,
            sample_rate=44100,
            duration=1.0,
            frequency=440.0,
            amplitude=1.0,
            parameters={"test": "value"},
            data=[0.0, 0.1, 0.2],
        )
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)

        assert signal.id is not None
        assert signal.name == "Test Signal"
        assert signal.signal_type == SignalType.SINE
        assert signal.created_at is not None
        assert isinstance(signal.created_at, datetime)

    def test_create_analysis_result(self):
        signal = Signal(
            name="Test",
            signal_type=SignalType.SINE,
            sample_rate=1000,
            duration=1.0,
            data=[0.0] * 1000,
        )
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)

        analysis = AnalysisResult(
            signal_id=signal.id,
            analysis_type="fft",
            result_data={"frequencies": [0, 10], "magnitudes": [1.0, 0.5]},
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        assert analysis.id is not None
        assert analysis.signal_id == signal.id
        assert analysis.analysis_type == "fft"
        assert analysis.created_at is not None

    def test_create_audit_log(self):
        audit = AuditLog(
            user_id="user123",
            action="create",
            resource_type="signal",
            resource_id="1",
            details="Created test signal",
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)

        assert audit.id is not None
        assert audit.user_id == "user123"
        assert audit.action == "create"
        assert audit.timestamp is not None

    def test_signal_type_enum(self):
        assert SignalType.SINE == "sine"
        assert SignalType.SQUARE == "square"
        assert SignalType.NOISE == "noise"
        assert SignalType.CHIRP == "chirp"

    def test_signal_relationships(self):
        signal = Signal(
            name="Rel Test",
            signal_type=SignalType.SINE,
            sample_rate=1000,
            duration=1.0,
            data=[0.0] * 1000,
        )
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)

        analysis1 = AnalysisResult(signal_id=signal.id, analysis_type="fft", result_data={})
        analysis2 = AnalysisResult(signal_id=signal.id, analysis_type="statistics", result_data={})
        self.db.add_all([analysis1, analysis2])
        self.db.commit()

        analyses = self.db.query(AnalysisResult).filter(AnalysisResult.signal_id == signal.id).all()
        assert len(analyses) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])