import pytest
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.signal_processor import SignalProcessor
class TestSignalProcessor:
    def test_generate_sine_wave(self):
        data = SignalProcessor.generate_signal("sine", 1000, 1.0, frequency=10.0, amplitude=2.0)
        assert len(data) == 1000
        assert np.allclose(np.max(np.abs(data)), 2.0, atol=0.1)

    def test_generate_square_wave(self):
        data = SignalProcessor.generate_signal("square", 1000, 1.0, frequency=10.0, amplitude=1.0)
        assert len(data) == 1000
        assert np.allclose(np.max(np.abs(data)), 1.0, atol=0.1)

    def test_generate_noise_white(self):
        data = SignalProcessor.generate_signal("noise", 1000, 1.0, parameters={"noise_type": "white"}, amplitude=1.0)
        assert len(data) == 1000
        assert np.abs(np.mean(data)) < 0.2

    def test_generate_noise_pink(self):
        data = SignalProcessor.generate_signal("noise", 1000, 1.0, parameters={"noise_type": "pink"}, amplitude=1.0)
        assert len(data) == 1000

    def test_generate_noise_brown(self):
        data = SignalProcessor.generate_signal("noise", 1000, 1.0, parameters={"noise_type": "brown"}, amplitude=1.0)
        assert len(data) == 1000

    def test_generate_chirp(self):
        data = SignalProcessor.generate_signal("chirp", 1000, 1.0, frequency=100.0, parameters={"f0": 10, "f1": 500})
        assert len(data) == 1000

    def test_compute_fft(self):
        t = np.linspace(0, 1, 1000)
        data = np.sin(2 * np.pi * 10 * t).tolist()
        result = SignalProcessor.compute_fft(data, 1000)
        assert "frequencies" in result
        assert "magnitudes" in result
        assert "phases" in result
        assert len(result["frequencies"]) == 500

    def test_compute_spectrogram(self):
        data = np.random.randn(1000).tolist()
        result = SignalProcessor.compute_spectrogram(data, 1000, nperseg=256)
        assert "frequencies" in result
        assert "times" in result
        assert "spectrogram" in result

    def test_compute_statistics(self):
        data = np.random.randn(1000).tolist()
        result = SignalProcessor.compute_statistics(data)
        assert "mean" in result
        assert "std" in result
        assert "min" in result
        assert "max" in result
        assert "rms" in result
        assert "peak_to_peak" in result
        assert "skewness" in result
        assert "kurtosis" in result

    def test_design_fir_filter(self):
        taps = SignalProcessor.design_fir_filter(51, 1000, 8000)
        assert len(taps) == 51

    def test_design_iir_filter(self):
        b, a = SignalProcessor.design_iir_filter(4, 1000, 8000)
        assert len(b) == 5
        assert len(a) == 5

    def test_apply_filter(self):
        data = np.random.randn(1000).tolist()
        b, a = SignalProcessor.design_iir_filter(4, 1000, 8000)
        filtered = SignalProcessor.apply_filter(data, b, a)
        assert len(filtered) == 1000

    def test_detect_anomalies_global(self):
        data = np.zeros(100)
        data[50] = 10.0
        result = SignalProcessor.detect_anomalies(data.tolist(), threshold_std=2.0)
        assert 50 in result["anomaly_indices"]

    def test_detect_anomalies_windowed(self):
        data = np.zeros(200)
        data[50] = 10.0
        data[150] = 10.0
        result = SignalProcessor.detect_anomalies(data.tolist(), threshold_std=2.0, window_size=100)
        assert 50 in result["anomaly_indices"]
        assert 150 in result["anomaly_indices"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])