import streamlit as st
import plotly.express as px
from datetime import date
from core.db import init_db,list_farms,get_farm,get_events,get_observations,save_recommendation
from core.weather import get_weather
from core.waterbalance import run_balance
from core.decision import decide
from core.decision import ACTION_LABELS
from core.crops import crop_status
from core.ui import disclaimer,apply_css
st.set_page_config(page_title="Dashboard | JalRakshak",page_icon="📊",layout="wide"); apply_css()
init_db(); st.title("📊 Irrigation Dashboard"); farms=list_farms()
if not farms: st.warning("Set up a farm first."); st.page_link("pages/1_Farm_Setup.py",label="Open Farm Setup"); st.stop()
ids=[x["id"] for x in farms]; default=st.session_state.get("farm_id",ids[0]); fid=st.selectbox("Farm",ids,index=ids.index(default) if default in ids else 0,format_func=lambda x:next(f["name"] for f in farms if f["id"]==x)); farm=get_farm(fid)
try:
    weather,source,age=get_weather(farm["latitude"],farm["longitude"]); balance=run_balance(weather,farm,get_events(fid),get_observations(fid)); status=crop_status(farm["sowing_date"],harvest_date=farm["harvest_date"],crop=farm["crop"]); result=decide(balance,farm,status); save_recommendation(fid,date.today(),result,"Low" if "OFFLINE" in source else "Medium")
except Exception: st.error("Unable to prepare this advisory. Check the farm details and weather connection, then try again."); st.stop()
if "OFFLINE" in source: st.warning(source)
else: st.caption(source+(f" · cached {age} hours ago" if age else ""))
st.subheader(ACTION_LABELS[result["action"]])
for reason in result["reasons"]: st.write("• "+reason)
historical=balance[~balance.is_forecast]; current=historical.iloc[-1] if len(historical) else balance.iloc[0]
quality="Low" if "OFFLINE" in source else "Medium"
cols=st.columns(3); cols[0].metric("Estimated root-zone storage",f"{current.storage:.1f} mm"); cols[1].metric("Estimated crop use today",f"{current.etc:.1f} mm"); cols[2].metric("Data quality",quality,help="Input completeness and freshness; not probability that advice is correct.")
if result["gross_mm"] is not None:
    a,b=st.columns(2); a.metric("Estimated gross irrigation depth",f"{result['gross_mm']:.1f} mm"); b.metric("Estimated farm quantity",f"{result['litres']:.0f} L")
st.write("**Reassess:** "+result["reassess"]); st.caption("Data quality describes input completeness and freshness, not the probability that this recommendation is correct. With no observation, simulation starts at field capacity at the first weather date. Forecast rain is probability weighted.")
if not farm["harvest_date"]:
    from core.crops import estimated_harvest
    st.caption(f"Harvest date is estimated from the crop stages: {estimated_harvest(farm['crop'],date.fromisoformat(farm['sowing_date']))}. Local varieties and conditions can change this.")
if farm["crop"]=="Rice (paddy)": st.warning("Rice/paddy commonly uses standing water; this simplified model is less reliable for rice.")
with st.expander("How this is calculated"): st.write("Estimated crop use = crop coefficient × reference ET0. Available soil water is approximated from soil capacity × effective root depth. Rain, logged irrigation and optional field observations update estimated depletion. This is a simplified FAO-56-inspired model.")
st.plotly_chart(px.line(balance,x="date",y=["storage","raw"],labels={"value":"Water depth (mm)","date":"Date","variable":"Estimate"},title="Estimated root-zone storage and readily available threshold"),use_container_width=True)
st.subheader("Weather summary"); st.dataframe(weather.tail(10),use_container_width=True,hide_index=True); disclaimer()
