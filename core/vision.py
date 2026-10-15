"""Optional Gemini vision estimate from an in-memory field photo."""
import json
import requests
from .config import GEMINI_API_KEY,GEMINI_MODEL

def inspect_soil_photo(image_bytes,mime_type,soil_type,weather_summary):
    if not GEMINI_API_KEY:
        return None,"Add GEMINI_API_KEY in your local .env and restart the app to enable photo analysis."
    prompt=("Assess only visible surface wetness cues in this close-up farm soil photo. Ignore soil colour completely. "
            "Do not infer moisture from colour, location, crop, or weather; weather and mapped soil are context only. "
            "Use visible sheen, water film, clumping, stickiness evidence, cracks, crust, and loose dry texture. "
            "If the photo does not clearly show soil or cues are insufficient, return Unknown. Do not claim a photo can measure subsurface moisture. "
            "Return only JSON with keys condition (one of Likely wet, Moist, Slightly dry, Likely dry, Unknown) and note (one short sentence). "
            f"Mapped/manual soil type: {soil_type}. Weather context: {weather_summary}.")
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    try:
        response=requests.post(url,headers={"x-goog-api-key":GEMINI_API_KEY},json={"contents":[{"parts":[{"inline_data":{"mime_type":mime_type,"data":__import__('base64').b64encode(image_bytes).decode("ascii")}},{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json"}},timeout=20)
        response.raise_for_status(); text=response.json()["candidates"][0]["content"]["parts"][0]["text"]
        data=json.loads(text); allowed={"Likely wet","Moist","Slightly dry","Likely dry","Unknown"}
        if data.get("condition") not in allowed or not isinstance(data.get("note"),str): raise ValueError("Unexpected vision response")
        return data,None
    except (requests.RequestException,ValueError,KeyError,IndexError,TypeError):
        return None,"Photo analysis could not be completed. Check the API key and network, or use the weather estimate and a direct field check."
