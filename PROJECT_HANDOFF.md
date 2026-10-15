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
| 5a Weather harvest outlook, optional soil map/photo | Implemented; 28 tests pass | Crop-calendar date plus forecast rain watch. Optional SoilGrids lookup and camera/Gemini surface estimate; API key blank. SoilGrids REST availability is unreliable/current docs say paused. |
| 6 Digital Twin | Implemented; scenario unit test passes | Forecast-only scenario modifiers and presets. Optimizer not wired into UI. |
| 7 Offline UX + core tests | Basic suite passes | 18 tests pass; mock coverage and page smoke tests still needed. |
| 8 ML forecast | Intentionally unavailable | No real training data. Keep separate surface-moisture target and honest fallback. |
| 9 Optimizer + Water Usage | Partial | CSV, logs/history, basic optimizer function; no tested schedule replay/baseline comparison. |
| 10 AI Agronomist | Partial | Deterministic fallback and optional Gemini request; API behavior not live-verified; credentials blank. |
| 11 UI polish/map | Partial | Green theme and Plotly charts. Map omitted. Check responsive rendering. |
| 12 Final QA + demo | Not done | Compile, tests, app launch, offline smoke run, docs review and demo rehearsal outstanding. |

## Latest UX pass

- Navigation groups Home, Set up your farm, and Today's advice under `GET STARTED`; Weather, scenarios, questions, and logs under `EXPLORE`.
- Home explains the two-step flow and has direct calls to action. Farm Setup uses everyday labels and explains soil and location fields. Dashboard leads with “What should I do today?”, a plain-language next step, understandable metrics, the input-quality definition, and optional calculation details.
- Page-level `st.set_page_config` calls were removed so the app shell owns page setup and grouped navigation.
- Streamlit dependency minimum is 1.50 because the refreshed UI uses the `width="stretch"` API.
- Runtime reported `TypeError` for unsupported `type=` on `st.page_link`; removed the argument from all page links. Home now uses a high-contrast green gradient hero, the app background has a soft green/gold gradient, and sidebar/card contrast was strengthened.
- Core tests and compilation rerun after this UX pass: 18 tests passed; compilation passed. Streamlit health endpoint returned HTTP 200 on `127.0.0.1:8765`; visual review is pending from the user because the browser policy denied my reload action.
- Dashboard workflow now explains field selection, surface outlook, irrigation advice, field notes, and harvest recording. Surface outlook uses recent observed daily weather and states it is not a soil measurement. Rules: >=5 mm latest observed day or >=8 mm over last three observed days means “Likely wet”; >=2 mm means “Likely drying”; no significant rain plus average high >=32°C or ET0 >=5 mm/day means “Likely dry”; warm, nearly rain-free days can show “Slightly dry.” Thresholds are illustrative and should be tuned against local field observations.
- “Record harvest today” stores date and selected field's saved place/coordinates, idempotently per field/day. This uses farm setup location; the app does not capture device GPS. A recorded harvest changes today's crop status to fallow for irrigation advice.
- Farm location controls were outside the submit form so changing a search query refreshes only after a deliberate Search click; location dropdown and coordinate-entry mode are always visible. Dashboard links directly to Farm Setup. Soil map/camera controls sit in a collapsed optional expander.
- 2026-10-16: Applied the user's dark glass UI concept to the app shell and Dashboard. Sidebar starts collapsed; the recommendation and wet/dry status are computed from the selected farm's weather and crop data. No mock/example numbers are shown as live data.
- 2026-10-16: Simplified Dashboard after user screenshot feedback. Removed technical metric tiles (root-zone %, ETc, rain totals, crop stage), large harvest weather panel, and two charts from the main view. Main page now focuses on field surface wet/dry status, one non-redundant next action, compact harvest date, and optional harvest record. Soil map/photo remain collapsed and optional.
- Harvest timing shows the crop-calendar or entered expected date plus a near-date rain watch; it does not claim forecast weather can prove crop maturity. Camera input is held in memory for the page session and photo analysis is optional Gemini vision; prompt explicitly excludes colour as a moisture cue. API key remains blank.
- 2026-10-16 verification: `python -m compileall app.py pages core tests` passed; `python -m pytest --basetemp=.pytest-tmp -q` passed (**28 passed**); `git diff --check` passed with only CRLF normalization warnings. Live-mode Streamlit is running on `127.0.0.1:8766`; `/_stcore/health` returned HTTP 200. Port 8765 was unavailable when starting the revised live-mode process. Live weather still depends on API/network reachability; fallback uses cache or visibly labelled sample weather.
- AppTest smoke run for the standalone farm page did not return within the 15-second timeout; no page-render pass is claimed. The location picker logic and server health were checked; visual review remains with the user.

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
- Photo classification requires `GEMINI_API_KEY` and internet. No key is in the repo; captured photos are not persisted. SoilGrids lookup is best-effort and currently may be unavailable; manually selected soil remains the fallback.

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
