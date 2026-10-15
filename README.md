# JalRakshak AI

**Predict the Need. Save Every Drop.** A software-only irrigation advisory prototype. It estimates root-zone water from weather, crop and soil assumptions, irrigation logs and optional field observations. It does not use sensors or measure the soil.

## Run locally

Requires Python 3.10 or newer.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Set `JALRAKSHAK_OFFLINE=1` in `.env` for the clearly labelled bundled Hyderabad sample data. Default mode attempts Open-Meteo, then uses a successful local cache, then sample data. No weather API key is expected for the selected public endpoints. Optional Gemini answers require `GEMINI_API_KEY`; leave it blank for offline explanations. Never commit `.env` or put secrets in source.

Weather requests follow the [Open-Meteo forecast API](https://open-meteo.com/en/docs) and [geocoding API](https://open-meteo.com/en/docs/geocoding-api). The optional Gemini REST request follows the [official generateContent API](https://ai.google.dev/api/generate-content); its model name remains configurable.

The app creates its SQLite database at `data/jalrakshak.sqlite3` on first run. Back up or delete that file as needed; it is ignored by Git.

## Checks

```bash
python -m compileall .
pytest -q
streamlit run app.py
```

The test suite is designed to run without internet. Live API availability depends on network access.

## Pages

- Farm Setup: create and manage local farm profiles.
- Farm location: search for a town/village and choose a match, or enter coordinates manually. The selected coordinates power weather, harvest timing, and optional mapped soil.
- Dashboard: step-by-step guidance, weather-based surface wet/dry outlook, irrigation recommendation, water estimate, and optional harvest record tied to the saved farm location.
- Weather Intelligence: daily weather series with source/fallback labels.
- Digital Twin: simulated forecast-only scenarios.
- AI Agronomist: deterministic explanation; optional Gemini API.
- Water Usage: irrigation and field observation logs, history, and CSV export.

## Limitations

All root-zone quantities are estimates. Crop and soil parameters are simplified; rainfall effectiveness and irrigation efficiency are assumptions. Forecasts can be wrong. Rice/paddy is less suitable for this balance model. Scenario outputs are simulations. No ML forecast is claimed because a suitable validated historical training dataset is not bundled. Simulated comparisons are not proof of water savings. Consult local agricultural guidance and inspect field soil before acting.

See [DOCUMENTATION.md](JalRakshak_AI_Documentation.md) for the concept, and [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) for the durable status log and remaining work.
