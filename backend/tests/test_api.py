import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestSignalAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_generate_sine_signal(self):
        response = client.post(
            "/api/signals/generate",
            json={
                "name": "Test Sine",
                "signal_type": "sine",
                "sample_rate": 1000,
                "duration": 1.0,
                "frequency": 10.0,
                "amplitude": 1.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Sine"
        assert data["signal_type"] == "sine"
        assert data["sample_rate"] == 1000
        assert len(data["data"]) == 1000

    def test_generate_square_signal(self):
        response = client.post(
            "/api/signals/generate",
            json={
                "name": "Test Square",
                "signal_type": "square",
                "sample_rate": 1000,
                "duration": 1.0,
                "frequency": 10.0,
            },
        )
        assert response.status_code == 200
        assert response.json()["signal_type"] == "square"

    def test_generate_noise_signal(self):
        response = client.post(
            "/api/signals/generate",
            json={
                "name": "Test Noise",
                "signal_type": "noise",
                "sample_rate": 1000,
                "duration": 1.0,
            },
        )
        assert response.status_code == 200
        assert response.json()["signal_type"] == "noise"

    def test_generate_chirp_signal(self):
        response = client.post(
            "/api/signals/generate",
            json={
                "name": "Test Chirp",
                "signal_type": "chirp",
                "sample_rate": 1000,
                "duration": 1.0,
                "parameters": {"f0": 10, "f1": 500},
            },
        )
        assert response.status_code == 200
        assert response.json()["signal_type"] == "chirp"

    def test_generate_signal_invalid_type(self):
        response = client.post(
            "/api/signals/generate",
            json={
                "name": "Test",
                "signal_type": "invalid",
                "sample_rate": 1000,
                "duration": 1.0,
            },
        )
        assert response.status_code == 422

    def test_generate_signal_invalid_params(self):
        response = client.post(
            "/api/signals/generate",
            json={
                "name": "Test",
                "signal_type": "sine",
                "sample_rate": -1,
                "duration": 1.0,
            },
        )
        assert response.status_code == 422

    def test_list_signals(self):
        client.post(
            "/api/signals/generate",
            json={"name": "S1", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        response = client.get("/api/signals")
        assert response.status_code == 200
        signals = response.json()
        assert len(signals) >= 1

    def test_list_signals_filter_by_type(self):
        response = client.get("/api/signals?signal_type=sine")
        assert response.status_code == 200
        signals = response.json()
        assert all(s["signal_type"] == "sine" for s in signals)

    def test_get_signal(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Get Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.get(f"/api/signals/{signal_id}")
        assert response.status_code == 200
        assert response.json()["id"] == signal_id

    def test_get_signal_not_found(self):
        response = client.get("/api/signals/99999")
        assert response.status_code == 404

    def test_delete_signal(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Delete Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.delete(f"/api/signals/{signal_id}")
        assert response.status_code == 200
        get_resp = client.get(f"/api/signals/{signal_id}")
        assert get_resp.status_code == 404

    def test_analyze_fft(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "FFT Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.post(
            "/api/signals/analyze",
            json={"signal_id": signal_id, "analysis_type": "fft"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_type"] == "fft"
        assert "frequencies" in data["result_data"]
        assert "magnitudes" in data["result_data"]

    def test_analyze_spectrogram(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Spec Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.post(
            "/api/signals/analyze",
            json={"signal_id": signal_id, "analysis_type": "spectrogram", "parameters": {"nperseg": 128}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_type"] == "spectrogram"
        assert "spectrogram" in data["result_data"]

    def test_analyze_statistics(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Stats Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.post(
            "/api/signals/analyze",
            json={"signal_id": signal_id, "analysis_type": "statistics"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_type"] == "statistics"
        assert "mean" in data["result_data"]
        assert "std" in data["result_data"]

    def test_analyze_invalid_type(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.post(
            "/api/signals/analyze",
            json={"signal_id": signal_id, "analysis_type": "invalid"},
        )
        assert response.status_code in (400, 422)

    def test_analyze_nonexistent_signal(self):
        response = client.post(
            "/api/signals/analyze",
            json={"signal_id": 99999, "analysis_type": "fft"},
        )
        assert response.status_code == 400

    def test_list_analyses(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "List Analysis", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        client.post("/api/signals/analyze", json={"signal_id": signal_id, "analysis_type": "fft"})
        client.post("/api/signals/analyze", json={"signal_id": signal_id, "analysis_type": "statistics"})
        response = client.get(f"/api/signals/{signal_id}/analyses")
        assert response.status_code == 200
        analyses = response.json()
        assert len(analyses) >= 2

    def test_export_json(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Export Test", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.get(f"/api/signals/{signal_id}/export?format=json&include_analysis=false")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == signal_id
        assert "data" in data

    def test_export_csv(self):
        create_resp = client.post(
            "/api/signals/generate",
            json={"name": "Export CSV", "signal_type": "sine", "sample_rate": 1000, "duration": 1.0, "frequency": 10.0},
        )
        signal_id = create_resp.json()["id"]
        response = client.get(f"/api/signals/{signal_id}/export?format=csv")
        assert response.status_code == 200

    def test_pagination(self):
        for i in range(15):
            client.post(
                "/api/signals/generate",
                json={"name": f"Page {i}", "signal_type": "sine", "sample_rate": 1000, "duration": 0.1, "frequency": 10.0},
            )
        response = client.get("/api/signals?skip=0&limit=10")
        assert response.status_code == 200
        assert len(response.json()) == 10
        response = client.get("/api/signals?skip=10&limit=10")
        assert len(response.json()) >= 5