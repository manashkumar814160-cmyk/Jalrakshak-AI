"""Best-effort SoilGrids soil texture lookup; keep manual farm soil as fallback."""
from functools import lru_cache
import requests

URL="https://rest.isric.org/soilgrids/v2.0/properties/query"

def texture_class(sand,clay):
    sand=float(sand); clay=float(clay)
    if sand>=70: return "Sandy"
    if clay>=40: return "Clay"
    if clay>=27 and sand<45: return "Clay loam"
    if sand>=43 and clay<20: return "Sandy loam"
    return "Loamy"

@lru_cache(maxsize=128)
def lookup_soil(latitude,longitude):
    """Fetch approximate topsoil texture at a coordinate; gracefully report outages."""
    try:
        response=requests.get(URL,params={"lat":latitude,"lon":longitude,"property":["sand","clay"],"depth":"0-5cm","value":"mean"},timeout=8)
        response.raise_for_status(); payload=response.json()
        layers=payload["properties"]["layers"]
        values={}
        for layer in layers:
            name=layer.get("name","").lower()
            depth=layer.get("depths",[{}])[0]
            val=depth.get("values",{}).get("mean")
            if name in ("sand","clay") and val is not None: values[name]=val/10
        if not {"sand","clay"}.issubset(values): raise ValueError("Soil texture values unavailable")
        return {"soil":texture_class(values["sand"],values["clay"]),"sand_pct":values["sand"],"clay_pct":values["clay"],"source":"SoilGrids 250 m model estimate"}
    except (requests.RequestException,ValueError,KeyError,TypeError,IndexError):
        return None
