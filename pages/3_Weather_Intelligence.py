import streamlit as st
import plotly.express as px
from core.db import init_db,list_farms,get_farm
from core.weather import get_weather
from core.ml import forecast_surface_moisture
from core.ui import apply_css
st.set_page_config(page_title="Weather | JalRakshak",page_icon="🌦",layout="wide"); apply_css()
init_db(); st.title("🌦 Weather Intelligence"); farms=list_farms()
if not farms: st.info("Set up a farm to view local weather."); st.stop()
fid=st.selectbox("Farm",[f["id"] for f in farms],format_func=lambda x:next(f["name"] for f in farms if f["id"]==x)); farm=get_farm(fid)
try:
    df,source,age=get_weather(farm["latitude"],farm["longitude"]); st.warning(source) if "OFFLINE" in source else st.caption(source+(f" · {age} hours old" if age else ""))
    st.plotly_chart(px.bar(df,x="date",y="rain",labels={"rain":"Rain (mm)","date":"Date"},title="Daily rainfall"),use_container_width=True)
    st.plotly_chart(px.line(df,x="date",y=["tmax","tmin"],labels={"value":"Temperature (°C)","date":"Date","variable":"Series"},title="Daily temperature"),use_container_width=True)
    if df["sm_model"].notna().any():
        st.plotly_chart(px.line(df,x="date",y="sm_model",labels={"sm_model":"Modelled surface moisture (m³/m³)","date":"Date"},title="Open-Meteo modelled surface soil moisture, 0–7 cm"),use_container_width=True)
        st.caption("This modelled surface-layer value is separate from estimated root-zone storage in millimetres.")
    ml=forecast_surface_moisture(df.dropna(subset=["sm_model"]))
    st.info(ml["message"])
    st.dataframe(df,use_container_width=True,hide_index=True)
except Exception as e: st.error(f"Weather is unavailable: {e}")
