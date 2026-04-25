# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-24

### Added
- Initial swarm-lab FastAPI service (`/`, `/fortune`, `/fortune/{id}`, `/crash`, `/health`).
- Structured JSON logging to Seq via `app/logger.py`.
- CI via GitHub Actions (pytest on push + PR).
- Intentional crash endpoint + one deliberately flaky test for fleet signalling.
