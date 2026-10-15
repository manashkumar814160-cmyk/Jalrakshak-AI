# Decisions and assumptions

- No sensors are present; root-zone quantities are estimates only.
- Crop coefficients, root growth, readily available water, effective rain, observation resets and irrigation efficiencies use the approximate values in `JalRakshak_AI_Master_Prompt.md`.
- When root depth increases, existing depletion is scaled proportionally to new root-zone capacity; newly accessed soil is treated as having the same fractional depletion as the existing zone.
- Simulation begins at field capacity on the first available weather date in the absence of a farmer observation.
- Forecast effective rain is weighted by daily rain probability; pessimistic mode credits no forecast rain.
- Gemini is optional and its key is intentionally unset. Deterministic explanatory fallback keeps the core usable without credentials.
- No trustworthy labeled training set was supplied. We do not download or train on unrelated/invented data, and we report no ML score.
- Weather sample is synthetic demonstration data, clearly labelled, not for model training.
- Costly or paid APIs are not required. The app uses the public Open-Meteo endpoints with timeout and local fallback.
- Git initialization/phase commits depend on repository status; currently this folder may not have Git metadata. See `PROJECT_HANDOFF.md`.
