import streamlit as st
import plotly.express as px
from core.db import init_db,list_farms,get_farm,get_events,get_observations,history,add_irrigation,add_observation
from core.weather import get_weather
from core.waterbalance import run_balance
from core.ui import apply_css
st.set_page_config(page_title="Water Usage | JalRakshak",page_icon="💧",layout="wide"); apply_css()
init_db(); st.title("💧 Water Usage & History"); farms=list_farms()
if not farms: st.info("Set up a farm first."); st.stop()
fid=st.selectbox("Farm",[f['id'] for f in farms],format_func=lambda x:next(f['name'] for f in farms if f['id']==x)); farm=get_farm(fid)
with st.expander("Log irrigation"):
    with st.form("irrigation"):
        d=st.date_input("Date"); amount=st.number_input("Gross depth (mm)",min_value=0.0,value=10.0); method=st.selectbox("Method",["Drip","Sprinkler","Flood/furrow"]); note=st.text_input("Note"); ok=st.form_submit_button("Save irrigation")
        if ok: add_irrigation(fid,d.isoformat(),amount,method,note); st.success("Saved irrigation log.")
with st.expander("Record field observation"):
    with st.form("observation"):
        od=st.date_input("Observation date",key="odate"); state=st.selectbox("Soil feels",["dry","moist","wet"]); ok2=st.form_submit_button("Save observation")
        if ok2: add_observation(fid,od.isoformat(),state); st.success("Saved observation.")
weather,source,_=get_weather(farm['latitude'],farm['longitude']); bal=run_balance(weather,farm,get_events(fid),get_observations(fid)); st.caption(f"Estimated balance · {source}")
metrics=st.columns(4); metrics[0].metric("Logged irrigation",f"{sum(x['gross_mm'] for x in get_events(fid)):.1f} mm"); metrics[1].metric("Effective rain in view",f"{bal.peff.sum():.1f} mm"); metrics[2].metric("Estimated crop use",f"{bal.eta.sum():.1f} mm"); metrics[3].metric("Estimated drainage",f"{bal.drainage.sum():.1f} mm")
st.plotly_chart(px.line(bal,x='date',y='depletion',labels={'depletion':'Estimated depletion (mm)','date':'Date'},title='Estimated root-zone depletion'),use_container_width=True); st.download_button("Download daily balance CSV",bal.to_csv(index=False),file_name="jalrakshak_daily_balance.csv",mime="text/csv")
st.subheader("Recommendation history"); h=history(fid); st.dataframe(h,use_container_width=True,hide_index=True) if h else st.info("No recommendations recorded yet. Open Dashboard to save today’s recommendation.")
