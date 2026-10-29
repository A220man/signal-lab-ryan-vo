# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-10-22

### Added
- FastAPI backend with signal generation API (sine, square, noise, chirp)
- Signal analysis endpoints (FFT, spectrogram, statistics)
- SQLite persistence with SQLAlchemy models
- React + TypeScript + Vite frontend with signal generator, list, and detail views
- Chart.js visualizations for time-domain and frequency-domain signals
- Docker Compose with backend, frontend, and Keycloak
- Comprehensive backend test suite (40 tests: API, models, signal processor)
- Frontend component tests (3 tests with Vitest + React Testing Library)
- Portfolio manifest (portfolio.json)

### Fixed
- CSV export endpoint now returns proper CSV format with correct media type and Content-Disposition header

### Signal Processing Engine
- Deterministic signal generation without LLM dependencies
- Voss-McCartney pink noise algorithm
- FFT with configurable windowing
- Spectrogram via STFT
- Statistical moments (mean, std, RMS, skewness, kurtosis)
- FIR/IIR filter design and application
- Anomaly detection (global and windowed)
