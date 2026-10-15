import json, time, hashlib
from datetime import date, timedelta
import requests
import pandas as pd
from .config import OFFLINE, CACHE_DIR, SAMPLE_WEATHER

PRESETS=[{"name":"Hyderabad","latitude":17.385,"longitude":78.4867,"country":"India"},{"name":"Warangal","latitude":17.9689,"longitude":79.5941,"country":"India"}]
_PLACE_CACHE={}
BASE="https://api.open-meteo.com/v1/forecast"
GEO="https://geocoding-api.open-meteo.com/v1/search"

def search_places(name):
    if OFFLINE or not name.strip(): return PRESETS
    cache_key=name.strip().casefold()
    if cache_key in _PLACE_CACHE: return _PLACE_CACHE[cache_key]
    try:
        r=requests.get(GEO,params={"name":name,"count":8,"language":"en","format":"json"},timeout=8); r.raise_for_status()
        results=[{"name":x["name"],"latitude":x["latitude"],"longitude":x["longitude"],"country":x.get("country","")} for x in r.json().get("results",[])] or PRESETS
        _PLACE_CACHE[cache_key]=results
        return results
    except (requests.RequestException,ValueError,KeyError): return [x for x in PRESETS if name.lower() in x["name"].lower()] or PRESETS

def _sample():
    with open(SAMPLE_WEATHER,encoding="utf-8") as f: raw=json.load(f)
    df=pd.DataFrame(raw["daily"])
    dates=pd.date_range(date.today()-timedelta(days=59),periods=len(df),freq="D")
    df["date"]=dates
    df["is_forecast"]=df.index >= max(0,len(df)-7)
    return df, "OFFLINE DEMO DATA — sample weather", 0

def _normalize(payload):
    d=payload["daily"]; n=len(d["time"])
    def col(k,default=None):
        vals=d.get(k,[default]*n)
        if vals is None or len(vals)!=n: return [default]*n
        return vals
    frame=pd.DataFrame({"date":pd.to_datetime(d["time"]),"tmax":col("temperature_2m_max"),"tmin":col("temperature_2m_min"),"rain":col("precipitation_sum",0),"rain_prob":col("precipitation_probability_max"),"et0":col("et0_fao_evapotranspiration"),"humidity":col("relative_humidity_2m_mean"),"wind":col("wind_speed_10m_max"),"sm_model":col("soil_moisture_0_to_7cm_mean")})
    frame["is_forecast"]=frame.date.dt.date >= date.today()
    for c in ["tmax","tmin","rain","et0"]: frame[c]=pd.to_numeric(frame[c],errors="coerce")
    if frame.empty or frame[["date","et0"]].isna().any().any(): raise ValueError("Weather response is missing required dates or ET0")
    return frame

def get_weather(latitude,longitude,past_days=60,forecast_days=7):
    if not (-90<=float(latitude)<=90 and -180<=float(longitude)<=180): raise ValueError("Invalid coordinates")
    if OFFLINE: return _sample()
    CACHE_DIR.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256(f"{latitude:.4f},{longitude:.4f},{past_days},{forecast_days}".encode()).hexdigest()
    path=CACHE_DIR/f"{key}.json"
    params={"latitude":latitude,"longitude":longitude,"daily":"temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,et0_fao_evapotranspiration,relative_humidity_2m_mean,wind_speed_10m_max,soil_moisture_0_to_7cm_mean","timezone":"auto","past_days":past_days,"forecast_days":forecast_days}
    try:
        r=requests.get(BASE,params=params,timeout=10); r.raise_for_status(); payload=r.json(); frame=_normalize(payload)
        path.write_text(json.dumps({"saved":time.time(),"payload":payload}),encoding="utf-8")
        return frame,"Live weather",0
    except (requests.RequestException,ValueError,KeyError,TypeError):
        if path.exists():
            try:
                cached=json.loads(path.read_text(encoding="utf-8")); return _normalize(cached["payload"]),"Cached weather",int((time.time()-cached["saved"])/3600)
            except (ValueError,KeyError,TypeError): pass
        return _sample()
