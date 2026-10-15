# Build progress

Status is recorded in [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md). This log reflects actual work in this workspace. Tests are not marked passed until run and observed.

## Current snapshot

- Scaffold and core application implemented from the master prompt.
- `python -m compileall .`: passed.
- `python -m pytest --basetemp=.pytest-tmp -q`: 18 passed (2026-10-16).
- `streamlit run app.py` started its local server; HTTP health check and AppTest were blocked/stalled in this environment. See handoff log.
- UX pass: grouped navigation into “Get Started” and “Explore”; rewrote Home, Farm Setup, and Dashboard around a two-step farmer workflow with plain-language prompts and metrics.
- Minimum Streamlit requirement is now 1.50 for the explicit responsive widget sizing used by the refreshed UI.
- Fixed Home navigation crash: `st.page_link()` does not accept `type`; removed that unsupported argument from all page links.
- Replaced white canvas with pale green/gold gradient, dark green navigation sidebar, high-contrast hero panel, and raised cards. Visual browser review still pending.
- Dashboard now has a step-by-step usage guide, a separate rain/heat-based wet/dry surface estimate, and a “Record harvest today” action that saves the selected field location with the date. Uses saved farm location, not phone GPS.
- Added tests for wet/dry rules and harvest location persistence: 24 tests pass; compileall passes.
- Fixed Farm Setup location search: the town search and nearest-place dropdown now render before the farm form; press Search to refresh results, or enter coordinates. Added direct Dashboard link to change location. Soil map and camera moved under a collapsed optional section to reduce clutter.
- Added harvest weather watch, optional SoilGrids lookup, and live camera photo capture with optional Gemini vision (color explicitly excluded). API key stays blank; photo held in session only. Current test count: 28 passed; compile passed. Live-mode server at http://127.0.0.1:8766 returned HTTP 200. Port 8765 unavailable at launch.
- Optional live Gemini key remains blank by design.
- ML forecast intentionally unavailable pending real historical data and validation.
