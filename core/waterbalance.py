import pandas as pd
from .crops import CROPS,kc_for,root_depth,p_adjusted
from .soils import awc,efficiency

OBS_RESET={"wet":.10,"moist":.45,"dry":.80}
def run_balance(weather_df,farm,irrigation_events=None,observations=None,pessimistic=False):
    irrigation_events=irrigation_events or []; observations=observations or []
    crop=farm["crop"]; soil=farm["soil"]; sow=pd.Timestamp(farm["sowing_date"]); area=float(farm["area_acres"])
    events={str(pd.Timestamp(x["date"]).date()):float(x["gross_mm"])*efficiency(x["method"]) for x in irrigation_events}
    obs={str(pd.Timestamp(x["date"]).date()):x["state"] for x in observations}
    depletion=0.0; prev_taw=None; rows=[]
    for _,w in weather_df.sort_values("date").iterrows():
        day=pd.Timestamp(w["date"]); age=max(0,(day-sow).days); kc=kc_for(crop,age); etc=kc*float(w["et0"] or 0)
        root=root_depth(crop,age); taw=awc(soil)*root; p=p_adjusted(CROPS[crop].p,etc); raw=p*taw
        if prev_taw is not None and taw>prev_taw: depletion += (taw-prev_taw)*depletion/max(prev_taw,1e-9)
        depletion=min(taw,max(0,depletion)); key=str(day.date())
        if key in obs: depletion=OBS_RESET[obs[key]]*taw
        rain=float(w.get("rain",0) or 0); prob=w.get("rain_prob",None)
        peff=0 if rain<2 else .8*rain
        if bool(w.get("is_forecast",False)):
            if pessimistic: peff=0
            elif pd.notna(prob): peff*=max(0,min(1,float(prob)/100))
        irrig=events.get(key,0)
        # Apply water inputs first; any input beyond field capacity is drainage.
        available_input=peff+irrig
        drainage=max(0,available_input-depletion)
        before_et=max(0,depletion-available_input)
        ks=1 if before_et<=raw else max(0,(taw-before_et)/max(taw-raw,1e-9))
        eta=ks*etc
        depletion=min(taw,before_et+eta)
        rows.append({"date":day,"is_forecast":bool(w.get("is_forecast",False)),"tmax":w.get("tmax"),"tmin":w.get("tmin"),"rain":rain,"rain_prob":prob,"et0":float(w["et0"]),"kc":kc,"etc":etc,"eta":eta,"ks":ks,"root":root,"taw":taw,"raw":raw,"peff":peff,"irrigation_net":irrig,"drainage":drainage,"storage":taw-depletion,"depletion":depletion,"stress":depletion>raw})
        prev_taw=taw
    return pd.DataFrame(rows)
