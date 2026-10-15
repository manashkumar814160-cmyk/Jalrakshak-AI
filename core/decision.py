from .soils import efficiency,litres

ACTION_LABELS={"NO_CROP":"NO ACTIVE CROP","IRRIGATE_NOW":"IRRIGATE NOW","IRRIGATE_SOON":"IRRIGATE SOON","WAIT":"WAIT","SKIP_RAIN_EXPECTED":"RAIN EXPECTED — RECHECK"}

def decide(balance,farm,status="growing"):
    if status in ("not_yet_sown","fallow","harvested"): return {"action":"NO_CROP","reasons":["No active crop is recorded for today."],"net_mm":None,"gross_mm":None,"litres":None,"reassess":"After planting or recording the active crop."}
    if balance.empty: return {"action":"WAIT","reasons":["Weather projection is unavailable."],"net_mm":None,"gross_mm":None,"litres":None,"reassess":"Check weather data and try again."}
    historical=balance[~balance.is_forecast]
    today=historical.iloc[-1] if len(historical) else balance.iloc[0]
    future=balance[(balance.is_forecast)&(balance.date>today.date)]
    irrig=bool(today.depletion>today.raw)
    rainsoon=bool(((future.rain>=2)&(future.rain_prob.fillna(0)>=60)).head(3).any()) if len(future) else False
    if irrig and rainsoon: action="SKIP_RAIN_EXPECTED"; reasons=["Estimated depletion is above the crop threshold.","Meaningful rain is expected soon; recheck after rainfall."]
    elif irrig: action="IRRIGATE_NOW"; reasons=["Estimated root-zone depletion is above the readily available water threshold.","No sufficiently likely near-term rain was found."]
    else:
        crossed=future[future.depletion>future.raw]
        if len(crossed) and (crossed.iloc[0].date-today.date).days<=1: action="IRRIGATE_SOON"; reasons=["The projection approaches the crop water threshold within 24 hours."]
        else: action="WAIT"; reasons=["Estimated storage is currently above the crop threshold.","Reassess as the forecast changes."]
    net=max(0,float(today.depletion-today.raw)) if action in ("IRRIGATE_NOW","IRRIGATE_SOON") else None
    gross=net/efficiency(farm["irrigation_method"]) if net is not None else None
    if status=="late_stage":
        reasons.append("Near harvest: avoid a large irrigation based only on this estimate; follow crop-specific local guidance.")
        net=gross=None
    return {"action":action,"reasons":reasons,"net_mm":net,"gross_mm":gross,"litres":litres(gross,float(farm["area_acres"])) if gross is not None else None,"reassess":"After expected rain" if action=="SKIP_RAIN_EXPECTED" else ("Check with local agricultural guidance before watering." if status=="late_stage" else "Tomorrow, or sooner if conditions change.")}
