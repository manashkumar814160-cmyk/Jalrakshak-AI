import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
from html import escape
from core.db import init_db,list_farms,get_farm,get_events,get_observations,save_recommendation,mark_harvested_today,get_harvest_event
from core.weather import get_weather
from core.waterbalance import run_balance
from core.decision import decide
from core.decision import ACTION_LABELS
from core.crops import crop_status,CROPS
from core.ui import disclaimer
from core.field_condition import estimate_field_condition
from core.harvest import harvest_weather_outlook
from core.soil_lookup import lookup_soil
from core.vision import inspect_soil_photo
from core.config import GEMINI_API_KEY
init_db(); farms=list_farms()
if not farms:
    st.markdown('<section class="hero dashboard-hero"><div class="hero-kicker">JALRAKSHAK AI · FIELD DASHBOARD</div><h1>Know when it may be time to water.</h1><p>Set up a field location to see local weather, crop timing and a clear irrigation estimate.</p></section>',unsafe_allow_html=True)
    st.info("Add your field details first. It only takes about a minute.")
    st.page_link("pages/1_Farm_Setup.py",label="Set up your farm",icon="🌾")
    st.stop()
ids=[x["id"] for x in farms]; default=st.session_state.get("farm_id",ids[0]); fid=st.selectbox("Choose your field",ids,index=ids.index(default) if default in ids else 0,format_func=lambda x:next(f["name"] for f in farms if f["id"]==x)); farm=get_farm(fid)
st.markdown(f'<section class="hero dashboard-hero"><div class="hero-kicker">JALRAKSHAK AI · FIELD DASHBOARD</div><h1>{escape(farm["name"])}</h1><p>Weather and crop guidance for {escape(farm["place"])} · {escape(farm["crop"])}</p></section>',unsafe_allow_html=True)
st.caption(f"Using the saved field location: {farm['place']} ({farm['latitude']:.4f}, {farm['longitude']:.4f}).")
st.page_link("pages/1_Farm_Setup.py",label="Choose or change location",icon="📍")
with st.expander("How to use this page",expanded=True):
    st.markdown("1. Choose your field above.  2. Read **Field surface outlook** for a weather-based wet/dry estimate and **What should I do today?** for irrigation guidance.  3. Add watering or a field note under **Watering & field notes**.  4. If you harvested today, record it below.")
try:
    weather,source,age=get_weather(farm["latitude"],farm["longitude"]); balance=run_balance(weather,farm,get_events(fid),get_observations(fid)); status="fallow" if get_harvest_event(fid) else crop_status(farm["sowing_date"],harvest_date=farm["harvest_date"],crop=farm["crop"]); result=decide(balance,farm,status); save_recommendation(fid,date.today(),result,"Low" if "OFFLINE" in source else "Medium")
except Exception: st.error("Unable to prepare this advisory. Check the farm details and weather connection, then try again."); st.stop()
if "OFFLINE" in source: st.warning("Sample weather is being used for this demo. It is not a real forecast.")
else: st.caption(f"Weather source: {source}"+(f" · saved {age} hours ago" if age else ""))
condition=estimate_field_condition(weather)
with st.container(border=True):
    st.markdown("### Field surface outlook")
    st.subheader(condition["label"])
    st.write(condition["detail"])
    st.caption("Weather-based estimate from recent observed rainfall and temperature. This is not a soil measurement; check the field directly before watering.")
harvest=harvest_weather_outlook(weather,farm["crop"],farm["sowing_date"],farm.get("harvest_date"))
historical=balance[~balance.is_forecast]; current=historical.iloc[-1] if len(historical) else balance.iloc[0]
quality="Low" if "OFFLINE" in source else "Medium"
banner_class={"IRRIGATE_NOW":"recommend-danger","IRRIGATE_SOON":"recommend-warning","WAIT":"recommend-success","SKIP_RAIN_EXPECTED":"recommend-neutral","NO_CROP":"recommend-neutral"}.get(result["action"],"recommend-neutral")
headline=ACTION_LABELS[result["action"]]
amount=(f"Apply about {result['gross_mm']:.1f} mm · {result['litres']:.0f} litres for {farm['area_acres']:.2f} acres." if result["gross_mm"] is not None else result["reassess"])
reasons=" ".join(escape(str(reason)) for reason in result["reasons"])
st.markdown(f'<section class="recommend-banner {banner_class}"><h2>{escape(headline)}</h2><p>{escape(amount)}</p><p class="reason">{reasons}</p></section>',unsafe_allow_html=True)
recent_observed=weather.loc[~weather["is_forecast"].fillna(True)].tail(7)
rain_7d=float(recent_observed["rain"].fillna(0).sum()) if len(recent_observed) else 0.0
storage_pct=max(0,min(100,100*float(current.storage)/max(float(current.taw),1e-9)))
age_days=max(0,(date.today()-date.fromisoformat(farm["sowing_date"])).days)
stages=CROPS[farm["crop"]].stages
if status in ("fallow","not_yet_sown"): stage_label="Fallow" if status=="fallow" else "Not planted"
elif age_days<stages[0]: stage_label="Initial"
elif age_days<sum(stages[:2]): stage_label="Development"
elif age_days<sum(stages[:3]): stage_label="Mid"
elif age_days<sum(stages): stage_label="Late"
else: stage_label="Past expected harvest"
metric_cards=[(f"{storage_pct:.0f}%","Estimated storage",f"{current.storage:.1f} of {current.taw:.1f} mm in the modeled root zone"),(f"{current.etc:.1f} mm","Today's crop water use (ETc)","Weather-based estimate for the selected crop stage"),(f"{rain_7d:.1f} mm","Rain · last 7 observed days","Observed daily rainfall at the saved location"),(stage_label,"Crop stage",f"{farm['crop']} · {age_days} days after planting")]
cols=st.columns(4)
for col,(value,label,detail) in zip(cols,metric_cards):
    col.markdown(f'<div class="glass-card"><div class="value">{escape(value)}</div><div class="label">{escape(label)}</div><div class="card-detail">{escape(detail)}</div></div>',unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("#### Harvest timing and weather")
    h1,h2=st.columns([1,3]); h1.metric("Estimated harvest date",harvest["date"].strftime("%d %b %Y")); h2.markdown(f"**{harvest['status']}**  \n{harvest['detail']}")
    st.caption("Crop-calendar date plus weather watch; the forecast cannot confirm crop maturity.")
if result["gross_mm"] is not None:
    st.markdown("### If you decide to water")
    a,b=st.columns(2); a.metric("Estimated water depth",f"{result['gross_mm']:.1f} mm"); b.metric("Estimated amount for this field",f"{result['litres']:.0f} litres")
st.info("**When to check again:** "+result["reassess"])
st.caption("Water amounts are estimates. With no field note, the calculation starts by assuming the root zone was full at the beginning of the weather record.")
if not farm["harvest_date"]:
    from core.crops import estimated_harvest
    st.caption(f"Harvest date is estimated from the crop stages: {estimated_harvest(farm['crop'],date.fromisoformat(farm['sowing_date']))}. Local varieties and conditions can change this.")
if farm["crop"]=="Rice (paddy)": st.warning("Rice/paddy commonly uses standing water; this simplified model is less reliable for rice.")
st.markdown("### Harvested today?")
today_harvest=get_harvest_event(fid)
if today_harvest:
    st.success(f"Harvest recorded for {today_harvest['place']} today. The farm location ({today_harvest['latitude']:.4f}, {today_harvest['longitude']:.4f}) was saved with the record.")
    st.caption("The field outlook above still uses weather for this saved location. If you harvest another field, select it first.")
elif st.button("Record harvest today",help="Saves today's date and the selected field's saved location."):
    try:
        event=mark_harvested_today(fid)
        st.success(f"Harvest recorded for {event['place']} today. Saved field location: {event['latitude']:.4f}, {event['longitude']:.4f}.")
        st.rerun()
    except ValueError as exc: st.error(str(exc))
with st.expander("Optional: soil map and live photo estimate"):
    st.write("These optional checks add context. The main weather estimate and irrigation advice work without them.")
    mapped_soil=st.session_state.get(f"mapped_soil_{fid}")
    if st.button("Check mapped soil type for this location",key=f"soilmap{fid}"):
        with st.spinner("Checking the public soil map…"):
            mapped_soil=lookup_soil(round(float(farm["latitude"]),4),round(float(farm["longitude"]),4))
        if mapped_soil: st.session_state[f"mapped_soil_{fid}"]=mapped_soil
        else: st.warning("The public soil map is unavailable right now. Keep using the soil type you selected during setup.")
    if mapped_soil:
        st.info(f"Mapped estimate: **{mapped_soil['soil']}** topsoil (sand {mapped_soil['sand_pct']:.0f}%, clay {mapped_soil['clay_pct']:.0f}%) · {mapped_soil['source']}. Compare with what you know about the field; this map is approximate.")
    soil_for_photo=mapped_soil["soil"] if mapped_soil else farm["soil"]
    st.caption(f"Current soil context: {soil_for_photo}. The photo estimate is instructed to ignore soil colour.")
    photo=st.camera_input("Take a live close-up of bare soil",key=f"soilphoto{fid}")
    if photo:
        st.image(photo,caption="Photo held in this page session; it is not saved by the app.",width=360)
        if st.button("Estimate surface condition from photo",key=f"analyzesoil{fid}"):
            if not GEMINI_API_KEY:
                st.info("Photo capture works, but AI photo analysis needs a Gemini key in your local .env, then restart the app. The key field is blank by design.")
            else:
                summary=condition["label"]+": "+condition["detail"]
                result_photo,error=inspect_soil_photo(photo.getvalue(),photo.type,soil_for_photo,summary)
                if error: st.warning(error)
                else:
                    st.subheader("Photo-based surface estimate: "+result_photo["condition"])
                    st.write(result_photo["note"])
                    st.caption("Preliminary visual estimate only. The model is instructed to ignore colour; inspect the soil directly for confirmation.")
with st.expander("Why am I seeing this advice?"):
    st.write("We estimate how much water may be available near the crop roots from the crop's age, soil type, weather, and watering or field notes you enter. Rain forecasts are uncertain. The result is a guide, not a soil measurement.")
    st.write("Input quality describes how complete and recent the information is. It is not a confidence score.")
chart_data=balance.tail(21).copy()
chart_data["available_water_threshold"]=chart_data["taw"]-chart_data["raw"]
rain_etc=balance.tail(14)
left_chart,right_chart=st.columns(2)
with left_chart:
    st.markdown("### 📈 Root-zone storage")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=chart_data["date"],y=chart_data["storage"],name="Estimated storage",mode="lines",line={"color":"#10b981","width":3},fill="tozeroy",fillcolor="rgba(16,185,129,.08)"))
    fig.add_trace(go.Scatter(x=chart_data["date"],y=chart_data["available_water_threshold"],name="Stress threshold",mode="lines",line={"color":"#fb7185","width":2,"dash":"dash"}))
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(15,23,42,.35)",height=350,margin={"l":10,"r":10,"t":20,"b":10},legend={"orientation":"h","y":1.12},xaxis_title="Date",yaxis_title="Estimated water (mm)")
    st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
with right_chart:
    st.markdown("### 📊 Rain vs crop water use")
    fig2=make_subplots(specs=[[{"secondary_y":True}]])
    fig2.add_trace(go.Bar(x=rain_etc["date"],y=rain_etc["rain"],name="Rain",marker_color="#38bdf8",opacity=.8),secondary_y=False)
    fig2.add_trace(go.Scatter(x=rain_etc["date"],y=rain_etc["etc"],name="Crop water use (ETc)",mode="lines+markers",line={"color":"#fb923c","width":3},marker={"size":6}),secondary_y=True)
    fig2.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(15,23,42,.35)",height=350,margin={"l":10,"r":10,"t":20,"b":10},legend={"orientation":"h","y":1.12},barmode="overlay")
    fig2.update_yaxes(title_text="Rain (mm)",secondary_y=False); fig2.update_yaxes(title_text="ETc (mm)",secondary_y=True)
    st.plotly_chart(fig2,width="stretch",config={"displayModeBar":False})
st.page_link("pages/6_Water_Usage.py",label="Add a watering log or field note",icon="💧")
disclaimer()
