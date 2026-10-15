import streamlit as st
import plotly.express as px
from datetime import date
from core.db import init_db,list_farms,get_farm,get_events,get_observations,save_recommendation
from core.weather import get_weather
from core.waterbalance import run_balance
from core.decision import decide
from core.decision import ACTION_LABELS
from core.crops import crop_status
from core.ui import disclaimer,page_header
init_db(); farms=list_farms()
page_header("Step 2 · Today's advice", "A simple estimate for your selected field, with the reasons behind it.")
if not farms:
    st.info("Add your field details first. It only takes about a minute.")
    st.page_link("pages/1_Farm_Setup.py",label="Set up your farm",icon="🌾")
    st.stop()
ids=[x["id"] for x in farms]; default=st.session_state.get("farm_id",ids[0]); fid=st.selectbox("Which field?",ids,index=ids.index(default) if default in ids else 0,format_func=lambda x:next(f["name"] for f in farms if f["id"]==x)); farm=get_farm(fid)
try:
    weather,source,age=get_weather(farm["latitude"],farm["longitude"]); balance=run_balance(weather,farm,get_events(fid),get_observations(fid)); status=crop_status(farm["sowing_date"],harvest_date=farm["harvest_date"],crop=farm["crop"]); result=decide(balance,farm,status); save_recommendation(fid,date.today(),result,"Low" if "OFFLINE" in source else "Medium")
except Exception: st.error("Unable to prepare this advisory. Check the farm details and weather connection, then try again."); st.stop()
if "OFFLINE" in source: st.warning("Sample weather is being used for this demo. It is not a real forecast.")
else: st.caption(f"Weather source: {source}"+(f" · saved {age} hours ago" if age else ""))
with st.container(border=True):
    st.markdown("### What should I do today?")
    st.subheader(ACTION_LABELS[result["action"]])
    for reason in result["reasons"]: st.write("• "+reason)
historical=balance[~balance.is_forecast]; current=historical.iloc[-1] if len(historical) else balance.iloc[0]
quality="Low" if "OFFLINE" in source else "Medium"
st.markdown("### The estimate")
cols=st.columns(3); cols[0].metric("Water near crop roots",f"{current.storage:.1f} mm",help="Estimated root-zone water storage, not measured soil moisture."); cols[1].metric("Crop water use today",f"{current.etc:.1f} mm",help="Estimated from weather and crop stage."); cols[2].metric("Input quality",quality,help="How complete/fresh the inputs are. This is not the chance that the advice is correct.")
if result["gross_mm"] is not None:
    st.markdown("### If you decide to water")
    a,b=st.columns(2); a.metric("Estimated water depth",f"{result['gross_mm']:.1f} mm"); b.metric("Estimated amount for this field",f"{result['litres']:.0f} litres")
st.info("**When to check again:** "+result["reassess"])
st.caption("Water amounts are estimates. With no field note, the calculation starts by assuming the root zone was full at the beginning of the weather record.")
if not farm["harvest_date"]:
    from core.crops import estimated_harvest
    st.caption(f"Harvest date is estimated from the crop stages: {estimated_harvest(farm['crop'],date.fromisoformat(farm['sowing_date']))}. Local varieties and conditions can change this.")
if farm["crop"]=="Rice (paddy)": st.warning("Rice/paddy commonly uses standing water; this simplified model is less reliable for rice.")
with st.expander("Why am I seeing this advice?"):
    st.write("We estimate how much water may be available near the crop roots from the crop's age, soil type, weather, and watering or field notes you enter. Rain forecasts are uncertain. The result is a guide, not a soil measurement.")
    st.write("Input quality describes how complete and recent the information is. It is not a confidence score.")
st.plotly_chart(px.line(balance,x="date",y=["storage","raw"],labels={"value":"Estimated water depth (mm)","date":"Date","variable":"Estimate"},title="How estimated water near the roots may change"),width="stretch")
st.page_link("pages/6_Water_Usage.py",label="Add a watering log or field note",icon="💧")
disclaimer()
