# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — FastAPI/React skeleton with one end-to-end workflow

Status: done

Acceptance:
- Backend FastAPI app runs with health endpoint
- Frontend React+Vite app builds and serves
- One complete workflow: signal generation -> analysis -> export
- Docker compose with backend, frontend, Keycloak
- Basic tests passing

Implementation: `backend/app/main.py`, `backend/app/api/signals.py`, `backend/app/services/signal_processor.py`, `backend/app/services/signal_service.py`, `backend/app/models/signal.py`, `backend/app/models/schemas.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `frontend/src/App.tsx`, `frontend/src/components/SignalComponents.tsx`, `frontend/src/hooks/useSignals.ts`, `frontend/src/api/client.ts`, `frontend/src/types/api.ts`, `frontend/src/main.tsx`, `docker-compose.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`

Tests: `backend/tests/test_signal_processor.py`, `backend/tests/test_api.py`, `backend/tests/test_models.py`, `frontend/src/components/SignalComponents.test.tsx`

### signal-engine — Core signal processing engine (deterministic, offline)

Status: planned

Acceptance:
- Signal generation (sine, square, noise, chirp)
- FFT analysis with configurable windows
- Filter design (FIR/IIR) and application
- Spectrogram computation
- All algorithms work without LLM keys

### auth-oidc — OIDC authentication with Keycloak

Status: planned

Acceptance:
- Keycloak realm import provided
- Authorization code flow with PKCE
- Backend session management with HttpOnly cookies
- Frontend login/logout flow
- Role-based access (viewer/operator/admin)

### llm-adapters — LLM provider adapters (OpenAI-compatible, Anthropic, Gemini, Ollama)

Status: planned

Acceptance:
- Unified adapter interface
- OpenAI-compatible adapter
- Anthropic messages adapter
- Gemini generateContent adapter
- Ollama adapter
- Configurable via env, no hardcoded keys

### ml-workflows — Three AI/ML workflows: anomaly detection, signal classification, denoising evaluation

Status: planned

Acceptance:
- Anomaly detection using statistical thresholds
- Signal classification with lightweight model
- Denoising evaluation with SNR metrics
- Reproducible evaluation commands
- Results grounded in actual signal data

