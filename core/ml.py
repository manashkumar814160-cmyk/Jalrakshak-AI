"""Optional surface-moisture ML. No model or performance claim without real data."""
def forecast_surface_moisture(history):
    if history is None or len(history)<120:
        return {"available":False,"message":"ML forecast unavailable — the weather-based water-balance projection is still available."}
    return {"available":False,"message":"ML forecast unavailable — validated, suitable historical training data is not bundled."}
