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

Set `JALRAKSHAK_OFFLINE=1` in `.env` only when you want the clearly labelled bundled Hyderabad demo data. The free Open-Meteo forecast and geocoding endpoints require no API key. The app uses a recent saved response if the network is unavailable; with no real cached data, it shows an unavailable state rather than presenting another location's demo weather as a live forecast. Optional Gemini photo analysis requires `GEMINI_API_KEY`; leave it blank to keep that feature disabled. Never commit `.env` or put secrets in source.

Weather requests follow the free [Open-Meteo forecast API](https://open-meteo.com/en/docs) and [geocoding API](https://open-meteo.com/en/docs/geocoding-api); neither needs a key. The app asks for supported hourly soil layers and daily crop-water inputs, validates responses, caches by coordinates, and labels unavailable/demo data. The optional Gemini REST request follows the [official generateContent API](https://ai.google.dev/api/generate-content); its model name remains configurable.

The app creates its SQLite database at `data/jalrakshak.sqlite3` on first run. Back up or delete that file as needed; it is ignored by Git.

## Checks

```bash
python -m compileall .
pytest -q
streamlit run app.py
```

The test suite is designed to run without internet. Live API availability depends on network access.

## Main workflow

The sidebar keeps the app to three steps: Home, Set up field, and Today's field outlook. A separate Field notes page records watering and observed soil condition. On setup, choose a town, allow browser location after pressing **Use my current location**, or enter coordinates. Soil can be selected manually or estimated from the selected location. The dashboard provides a weather-based wet/dry outlook, irrigation guidance, estimated harvest timing, and a harvest record. Optional soil map/photo tools are kept out of the main workflow.

Older weather exploration, scenario, and question-answering pages are not linked from the simplified navigation.

## Limitations

All root-zone quantities are estimates. Crop and soil parameters are simplified; rainfall effectiveness and irrigation efficiency are assumptions. Forecasts can be wrong. Rice/paddy is less suitable for this balance model. Scenario outputs are simulations. No ML forecast is claimed because a suitable validated historical training dataset is not bundled. Simulated comparisons are not proof of water savings. Consult local agricultural guidance and inspect field soil before acting.

See [DOCUMENTATION.md](JalRakshak_AI_Documentation.md) for the concept, and [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) for the durable status log and remaining work.
