import pandas as pd
from core.waterbalance import run_balance
farm={"crop":"Tomato","soil":"Loamy","sowing_date":"2026-01-01","area_acres":1,"irrigation_method":"Drip"}
def weather(rain=0): return pd.DataFrame([{"date":pd.Timestamp("2026-01-31"),"et0":5,"rain":rain,"rain_prob":0,"is_forecast":False}])
def test_dry_and_rain_effect():
    dry=run_balance(weather(),farm,observations=[{"date":"2026-01-31","state":"dry"}]); wet=run_balance(weather(10),farm,observations=[{"date":"2026-01-31","state":"dry"}])
    assert dry.iloc[0].depletion>wet.iloc[0].depletion
    assert dry.iloc[0].storage+dry.iloc[0].depletion==dry.iloc[0].taw
def test_observation_reset():
    x=run_balance(weather(),farm,observations=[{"date":"2026-01-31","state":"wet"}]); assert x.iloc[0].depletion>0
