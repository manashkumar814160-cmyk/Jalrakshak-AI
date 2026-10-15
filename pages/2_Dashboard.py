import streamlit as st
from datetime import date
from html import escape

from core.config import GEMINI_API_KEY
from core.crops import crop_status
from core.db import (
    get_events, get_farm, get_harvest_event, get_observations, init_db,
    list_farms, mark_harvested_today, save_recommendation,
)
from core.decision import ACTION_LABELS, decide
from core.field_condition import estimate_field_condition
from core.harvest import harvest_weather_outlook
from core.soil_lookup import lookup_soil
from core.vision import inspect_soil_photo
from core.waterbalance import run_balance
from core.weather import get_weather

init_db()
farms = list_farms()
if not farms:
    st.markdown('<section class="hero dashboard-hero"><div class="hero-kicker">JALRAKSHAK AI · FIELD DASHBOARD</div><h1>Check your field</h1><p>Choose a field location and crop to see the local weather outlook.</p></section>', unsafe_allow_html=True)
    st.info("Start by saving your field location and crop.")
    st.page_link("pages/1_Farm_Setup.py", label="Set up a field", icon="🌾")
    st.stop()

ids = [farm["id"] for farm in farms]
default_id = st.session_state.get("farm_id", ids[0])
fid = st.selectbox(
    "Choose your field", ids,
    index=ids.index(default_id) if default_id in ids else 0,
    format_func=lambda farm_id: next(f["name"] for f in farms if f["id"] == farm_id),
)
st.session_state["farm_id"] = fid
farm = get_farm(fid)
st.markdown(
    f'<section class="hero dashboard-hero"><div class="hero-kicker">TODAY · {escape(farm["place"])}</div>'
    f'<h1>{escape(farm["name"])}</h1><p>{escape(farm["crop"])} · {farm["area_acres"]:.2f} acres</p></section>',
    unsafe_allow_html=True,
)
st.page_link("pages/1_Farm_Setup.py", label="Change field location or details", icon="📍")
st.caption("Choose a field, check its wet/dry outlook, then decide whether to water or record a harvest.")

try:
    weather, source, age = get_weather(farm["latitude"], farm["longitude"])
    events = get_events(fid)
    observations = get_observations(fid)
    status = "fallow" if get_harvest_event(fid) else crop_status(
        farm["sowing_date"], harvest_date=farm["harvest_date"], crop=farm["crop"],
    )
    balance = run_balance(weather, farm, events, observations)
    result = decide(balance, farm, status)
    save_recommendation(fid, date.today(), result, "Low" if "OFFLINE" in source else "Medium")
except Exception:
    st.error("Could not prepare today's field outlook. Check the saved field details and weather connection, then try again.")
    st.stop()

if "OFFLINE" in source:
    st.warning("Sample weather is shown. It is not a local forecast.")
else:
    st.caption(f"Weather: {source}" + (f" · saved {age} hours ago" if age else ""))

condition = estimate_field_condition(weather)
condition_style = {
    "Likely wet": "condition-wet",
    "Likely drying": "condition-drying",
    "Slightly dry": "condition-drying",
    "Likely dry": "condition-dry",
}.get(condition["label"], "condition-neutral")
st.markdown(
    f'<section class="condition-card {condition_style}"><div class="condition-kicker">FIELD SURFACE · RECENT WEATHER</div>'
    f'<h2>{escape(condition["label"])}</h2><p>{escape(condition["detail"])}</p>'
    '<small>Weather estimate only · check the soil before watering.</small></section>',
    unsafe_allow_html=True,
)

action_copy = {
    "NO_CROP": "No active crop is recorded for this field.",
    "IRRIGATE_NOW": "The estimate suggests water may be needed. Check the soil before watering.",
    "IRRIGATE_SOON": "Water may be needed soon. Check the field again tomorrow.",
    "WAIT": "No irrigation is suggested right now. Check again if conditions change.",
    "SKIP_RAIN_EXPECTED": "Rain may help soon. Check the field after it rains.",
}
action_style = {
    "IRRIGATE_NOW": "recommend-danger",
    "IRRIGATE_SOON": "recommend-warning",
    "WAIT": "recommend-success",
    "SKIP_RAIN_EXPECTED": "recommend-neutral",
    "NO_CROP": "recommend-neutral",
}.get(result["action"], "recommend-neutral")
watering_amount = ""
if result["gross_mm"] is not None:
    watering_amount = f"If you choose to water: about {result['gross_mm']:.1f} mm for this field ({result['litres']:.0f} litres)."
st.markdown(
    f'<section class="recommend-banner {action_style}"><h2>{escape(ACTION_LABELS[result["action"]].title())}</h2>'
    f'<p>{escape(action_copy[result["action"]])}</p>'
    + (f'<p class="reason">{escape(watering_amount)}</p>' if watering_amount else "")
    + '</section>',
    unsafe_allow_html=True,
)

harvest = harvest_weather_outlook(
    weather, farm["crop"], farm["sowing_date"], farm.get("harvest_date"),
)
harvest_line = f"Estimated harvest: {harvest['date'].strftime('%d %b %Y')}"
if harvest["status"] == "Estimated date has passed":
    harvest_line += " · check crop maturity in the field"
st.markdown(f"**{escape(harvest_line)}**")
if harvest["status"] in ("Rain watch near harvest", "No major rain in the current forecast window", "Forecast window unavailable"):
    st.caption(escape(harvest["status"] + ". " + harvest["detail"]))

today_harvest = get_harvest_event(fid)
if today_harvest:
    st.success(f"Harvest recorded today for {today_harvest['place']}.")
elif st.button("Record harvest today", help="Saves today's date and this field's saved location."):
    try:
        mark_harvested_today(fid)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))

with st.expander("Optional: use a soil map or take a soil photo"):
    st.caption("These checks are optional. The main weather outlook and watering advice work without them.")
    mapped_soil = st.session_state.get(f"mapped_soil_{fid}")
    if st.button("Check mapped soil type", key=f"soilmap{fid}"):
        with st.spinner("Checking the public soil map…"):
            mapped_soil = lookup_soil(round(float(farm["latitude"]), 4), round(float(farm["longitude"]), 4))
        if mapped_soil:
            st.session_state[f"mapped_soil_{fid}"] = mapped_soil
        else:
            st.info("The public soil map is unavailable right now. Keep the soil type selected during setup.")
    if mapped_soil:
        st.caption(f"Approximate mapped soil: {mapped_soil['soil']} · compare with the field itself.")
    soil_for_photo = mapped_soil["soil"] if mapped_soil else farm["soil"]
    photo = st.camera_input("Take a close-up of bare soil", key=f"soilphoto{fid}")
    if photo and st.button("Estimate surface from photo", key=f"analyzesoil{fid}"):
        if not GEMINI_API_KEY:
            st.info("Photo analysis needs a Gemini key in your local .env. Photo capture works without it; the key is blank by design.")
        else:
            visual, error = inspect_soil_photo(photo.getvalue(), photo.type, soil_for_photo, condition["label"])
            if error:
                st.info(error)
            else:
                st.write(f"Photo estimate: **{visual['condition']}** · {visual['note']}")
                st.caption("A visual estimate, not a soil measurement. The model is instructed to ignore colour.")

st.page_link("pages/6_Water_Usage.py", label="Add a watering log or field note", icon="💧")
