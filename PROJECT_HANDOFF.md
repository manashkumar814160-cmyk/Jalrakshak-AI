# JalRakshak AI — agent handoff and coordination log

Last updated: 2026-10-16 (Asia/Calcutta)

## Source of truth

Read `JalRakshak_AI_Documentation.md` first, then `JalRakshak_AI_Master_Prompt.md`. This file records what exists and what remains, to prevent repeated work. Update the phase table and verification section whenever work changes. Do not claim a check passed unless its command was run and its output reviewed.

## Coordination rules for the next agent

1. Inspect this handoff and `git status` before editing; avoid recreating completed files.
2. Work one phase at a time using BUILD → RUN → VERIFY → FIX → LOG → COMMIT → NEXT.
3. Keep domain calculations in `core/`, presentation in `pages/`; `core/` must not import Streamlit.
4. Add observed command output/date to the Verification log and record design deviations in `DECISIONS.md`.
5. Preserve the honesty constraints: estimates are not measurements, sample data is not training data, surface moisture is separate from root-zone millimetres, and simulated savings are not field savings.
6. Keep credentials blank in `.env.example`; never add secrets to source, logs, or this file.
7. Continue with outstanding P0 items before optional P1 work. Do not ask questions; make conservative assumptions and log them.

## Phase checklist

| Phase | Status | Notes |
|---|---|---|
| 0 Scaffold and runnable app | Implemented; server started | Streamlit landing page, theme, requirements, env template, ignore rules, pages; fresh Git repository initialized. |
| 1 Weather + offline fallback | Implemented; unit schema/sample checks pass | Open-Meteo geocoding/weather, timeout, cache, sample data, offline flag. Mock coverage still needed. |
| 2 Crop/soil calculations | Implemented; unit tests pass | Crop stages, root depth, adjusted p, soil water capacity, efficiencies, conversions. |
| 3 Water balance + decisions | Implemented; unit tests pass | Pure calculation module; uses actual use after stress coefficient. Broader mass-balance examples still needed. |
| 4 Database + farm setup | Implemented; CRUD unit test passes | SQLite CRUD, farm form, logs and observations. End-to-end restart persistence not manually checked. |
| 5 Dashboard + weather | Implemented; server started | Recommendation card, weather summary, chart and disclaimer. Data-quality grading is conservative (Medium live, Low sample). |
| 6 Digital Twin | Implemented; scenario unit test passes | Forecast-only scenario modifiers and presets. Optimizer not wired into UI. |
| 7 Offline UX + core tests | Basic suite passes | 18 tests pass; mock coverage and page smoke tests still needed. |
| 8 ML forecast | Intentionally unavailable | No real training data. Keep separate surface-moisture target and honest fallback. |
| 9 Optimizer + Water Usage | Partial | CSV, logs/history, basic optimizer function; no tested schedule replay/baseline comparison. |
| 10 AI Agronomist | Partial | Deterministic fallback and optional Gemini request; API behavior not live-verified; credentials blank. |
| 11 UI polish/map | Partial | Green theme and Plotly charts. Map omitted. Check responsive rendering. |
| 12 Final QA + demo | Not done | Compile, tests, app launch, offline smoke run, docs review and demo rehearsal outstanding. |

## Verification log

- Initial inspection: Python 3.12.10 available. Workspace had no Git repository; initialized a new `main` repository on 2026-10-16. No prior history existed.
- `python -m compileall .` completed successfully after implementation.
- `python -m pytest --basetemp=.pytest-tmp -q` completed: **18 passed**. The explicit basetemp is needed because the sandbox blocks pytest's default temp directory outside the workspace.
- `git diff --check` completed; only Git's Windows line-ending normalization warnings were emitted.
- `core.weather._sample()` returned 67 rows with expected columns and the `OFFLINE DEMO DATA — sample weather` source label.
- `python -m streamlit run app.py --server.headless true --server.port 8765` started Uvicorn and printed local/network URLs. The sandbox denied a local HTTP health request, so no browser or endpoint health check is claimed. Streamlit `AppTest` stalled before returning and was interrupted.
- Open-Meteo forecast/geocoding variables and Gemini REST path/header were checked against current official docs; Gemini default is configurable.
- Network downloads: no training data downloaded. Public weather API is used only at app runtime; synthetic bundled sample is for demo fallback only.

## Credentials / external setup

- `GEMINI_API_KEY=` intentionally blank in `.env.example`. Optional Gemini explanations work only after the owner places their key in a local, untracked `.env` file.
- `GEMINI_MODEL` defaults to `gemini-3.8-flash`; it can be changed in `.env` if account/model availability differs.
- No key expected for Open-Meteo public endpoints. Network can be unavailable; offline sample mode is provided.

## Known implementation gaps to address

- Audit the water-balance ordering: depletion should be updated using actual crop use `ETa` after stress coefficient calculation, and drainage/mass-balance should be confirmed with hand examples.
- Validate sample data schema and realistic date rebasing; sample is generated and must always remain visibly labelled.
- Add decision tests for all actions, rain-probability boundary, and quantity behavior.
- Add weather cache/sample/offline mock tests and missing data tests.
- Confirm Streamlit version supports all widgets used, especially optional date inputs and page links.
- Complete optimizer integration or clearly record it as deferred; don't call the function a validated schedule optimizer until independently checked.
- Audit UI error handling so external/provider errors never show raw stack traces.
- Add and run smoke checks after fixing code. Update this file with actual observed results.
- The project was built as one initial snapshot because no app/repository history existed; no phase-by-phase commits have been made yet. Create later phase commits after their checks pass.
