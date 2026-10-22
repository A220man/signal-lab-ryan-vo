import numpy as np
from scipy import signal as sp_signal
from scipy.fft import fft, fftfreq
from typing import List, Dict, Any, Optional, Tuple
import json


class SignalProcessor:
    @staticmethod
    def generate_signal(
        signal_type: str,
        sample_rate: int,
        duration: float,
        frequency: Optional[float] = None,
        amplitude: float = 1.0,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        params = parameters or {}

        if signal_type == "sine":
            freq = frequency or 440.0
            return amplitude * np.sin(2 * np.pi * freq * t)

        elif signal_type == "square":
            freq = frequency or 440.0
            duty = params.get("duty_cycle", 0.5)
            return amplitude * sp_signal.square(2 * np.pi * freq * t, duty=duty)

        elif signal_type == "noise":
            noise_type = params.get("noise_type", "white")
            if noise_type == "white":
                return amplitude * np.random.normal(0, 1, len(t))
            elif noise_type == "pink":
                return SignalProcessor._generate_pink_noise(len(t), amplitude)
            elif noise_type == "brown":
                return SignalProcessor._generate_brown_noise(len(t), amplitude)
            else:
                return amplitude * np.random.normal(0, 1, len(t))

        elif signal_type == "chirp":
            f0 = params.get("f0", frequency or 20.0)
            f1 = params.get("f1", frequency or 2000.0)
            method = params.get("method", "linear")
            return amplitude * sp_signal.chirp(t, f0, duration, f1, method=method)

        else:
            raise ValueError(f"Unknown signal type: {signal_type}")

    @staticmethod
    def _generate_pink_noise(n: int, amplitude: float) -> np.ndarray:
        # Voss-McCartney algorithm for pink noise
        rows = 16
        array = np.random.randn(rows, n)
        # Apply 1/f weighting per row
        for i in range(rows):
            array[i] *= 1.0 / (2 ** (i / 2))
        y = np.sum(array, axis=0)
        return amplitude * y / np.std(y) if np.std(y) > 0 else amplitude * y

    @staticmethod
    def _generate_brown_noise(n: int, amplitude: float) -> np.ndarray:
        y = np.cumsum(np.random.randn(n))
        return amplitude * y / np.std(y) if np.std(y) > 0 else amplitude * y

    @staticmethod
    def compute_fft(data: List[float], sample_rate: int) -> Dict[str, Any]:
        n = len(data)
        y = np.array(data)
        yf = fft(y)
        xf = fftfreq(n, 1 / sample_rate)

        pos_mask = xf >= 0
        xf_pos = xf[pos_mask]
        magnitudes = np.abs(yf[pos_mask])
        phases = np.angle(yf[pos_mask])

        return {
            "frequencies": xf_pos.tolist(),
            "magnitudes": magnitudes.tolist(),
            "phases": phases.tolist(),
            "sample_rate": sample_rate,
            "n_samples": n,
        }

    @staticmethod
    def compute_spectrogram(
        data: List[float],
        sample_rate: int,
        nperseg: int = 256,
        noverlap: Optional[int] = None,
        window: str = "hann",
    ) -> Dict[str, Any]:
        y = np.array(data)
        if noverlap is None:
            noverlap = nperseg // 2

        f, t, Sxx = sp_signal.spectrogram(
            y, fs=sample_rate, window=window, nperseg=nperseg, noverlap=noverlap
        )

        return {
            "frequencies": f.tolist(),
            "times": t.tolist(),
            "spectrogram": 10 * np.log10(Sxx + 1e-12).tolist(),
            "sample_rate": sample_rate,
        }

    @staticmethod
    def compute_statistics(data: List[float]) -> Dict[str, Any]:
        y = np.array(data)
        return {
            "mean": float(np.mean(y)),
            "std": float(np.std(y)),
            "min": float(np.min(y)),
            "max": float(np.max(y)),
            "rms": float(np.sqrt(np.mean(y**2))),
            "peak_to_peak": float(np.max(y) - np.min(y)),
            "skewness": float(SignalProcessor._skewness(y)),
            "kurtosis": float(SignalProcessor._kurtosis(y)),
        }

    @staticmethod
    def _skewness(data: np.ndarray) -> float:
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)

    @staticmethod
    def _kurtosis(data: np.ndarray) -> float:
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3

    @staticmethod
    def design_fir_filter(
        num_taps: int,
        cutoff: float,
        sample_rate: int,
        window: str = "hann",
        pass_zero: bool = True,
    ) -> np.ndarray:
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        return sp_signal.firwin(num_taps, normalized_cutoff, window=window, pass_zero=pass_zero)

    @staticmethod
    def design_iir_filter(
        order: int,
        cutoff: float,
        sample_rate: int,
        btype: str = "lowpass",
        ftype: str = "butter",
    ) -> Tuple[np.ndarray, np.ndarray]:
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = sp_signal.iirfilter(order, normalized_cutoff, btype=btype, ftype=ftype)
        return b, a

    @staticmethod
    def apply_filter(data: List[float], b: np.ndarray, a: np.ndarray) -> np.ndarray:
        return sp_signal.filtfilt(b, a, np.array(data))

    @staticmethod
    def detect_anomalies(
        data: List[float],
        threshold_std: float = 3.0,
        window_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        y = np.array(data)
        if window_size is None:
            mean = np.mean(y)
            std = np.std(y)
            anomalies = np.abs(y - mean) > threshold_std * std
            return {
                "anomaly_indices": np.where(anomalies)[0].tolist(),
                "anomaly_values": y[anomalies].tolist(),
                "threshold": threshold_std * std,
                "global_mean": float(mean),
                "global_std": float(std),
            }
        else:
            anomalies_list = []
            for i in range(0, len(y), window_size):
                window = y[i : i + window_size]
                if len(window) < 10:
                    continue
                mean = np.mean(window)
                std = np.std(window)
                local_anomalies = np.abs(window - mean) > threshold_std * std
                indices = np.where(local_anomalies)[0] + i
                anomalies_list.extend(indices)
            return {
                "anomaly_indices": anomalies_list,
                "anomaly_values": y[anomalies_list].tolist() if anomalies_list else [],
                "threshold_std": threshold_std,
                "window_size": window_size,
            }