from core.weather import _normalize,search_places
def test_weather_schema():
    p={"daily":{"time":["2026-01-01"],"temperature_2m_max":[20],"temperature_2m_min":[10],"precipitation_sum":[0],"et0_fao_evapotranspiration":[3]}}
    df=_normalize(p); assert df.iloc[0].tmax==20 and df.iloc[0].rain==0
def test_offline_geocoding_uses_presets(monkeypatch):
    import core.weather as w
    monkeypatch.setattr(w,"OFFLINE",True)
    assert search_places("nonexistent")==w.PRESETS
