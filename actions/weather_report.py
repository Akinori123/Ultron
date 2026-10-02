# actions/weather_report.py

import json
import urllib.request
import webbrowser
from urllib.parse import quote_plus
from typing import Dict, Any, Optional


_COND_PT = {
    "sunny": "ensolarado", "clear": "céu limpo", "partly cloudy": "parcialmente nublado",
    "cloudy": "nublado", "overcast": "encoberto", "mist": "névoa", "fog": "nevoeiro",
    "patchy rain nearby": "chuva passageira", "patchy rain possible": "possibilidade de chuva",
    "light rain": "chuva leve", "moderate rain": "chuva moderada", "heavy rain": "chuva forte",
    "light rain shower": "pancadas de chuva leve", "moderate or heavy rain shower": "pancadas de chuva",
    "thundery outbreaks possible": "possibilidade de trovoadas", "patchy light rain": "chuva leve passageira",
    "light drizzle": "garoa leve", "drizzle": "garoa", "rain": "chuva",
    "snow": "neve", "light snow": "neve leve", "heavy snow": "neve forte",
    "blizzard": "nevasca", "sleet": "chuva com neve",
    "patchy light drizzle": "garoa passageira", "freezing drizzle": "garoa congelante",
    "light freezing rain": "chuva congelante leve", "moderate snow": "neve moderada",
    "patchy snow possible": "possibilidade de neve", "patchy sleet possible": "possibilidade de chuva com neve",
    "patchy freezing drizzle possible": "possibilidade de garoa congelante",
    "heavy freezing drizzle": "garoa congelante forte", "moderate freezing rain": "chuva congelante moderada",
    "heavy freezing rain": "chuva congelante forte", "light sleet": "chuva com neve leve",
    "moderate sleet": "chuva com neve moderada", "heavy sleet": "chuva com neve forte",
    "light snow showers": "pancadas de neve leve", "moderate or heavy snow showers": "pancadas de neve",
    "light showers of ice pellets": "pancadas leves de granizo", "moderate or heavy showers of ice pellets": "pancadas de granizo",
    "patchy light snow": "neve leve passageira", "patchy moderate snow": "neve moderada passageira",
    "patchy heavy snow": "neve forte passageira", "moderate or heavy snow": "neve forte",
    "thundery outbreaks": "trovoadas", "torrential rain shower": "chuva torrencial",
}


def _cond_pt(desc: str) -> str:
    return _COND_PT.get((desc or "").strip().lower(), desc)


def get_live_weather(city: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches real-time live weather data using wttr.in with zero API keys required.
    Auto-detects device physical location dynamically via hardware/Wi-Fi and IP when no city is passed.
    Returns structured metrics: city, temp_c, condition, humidity, wind, and summary.
    """
    target_city = city.strip() if city and city.strip() else None
    if target_city and target_city.lower() in ("here", "my location", "current location", "auto", "local", "device"):
        target_city = None

    detected_lat = None
    detected_lon = None

    # Dynamically auto-detect physical device location
    if not target_city:
        try:
            from core.device_location import get_device_location
            loc = get_device_location()
            target_city = loc.get("city")
            detected_lat = loc.get("latitude")
            detected_lon = loc.get("longitude")
        except Exception as e:
            print(f"[Weather] Device location auto-detect notice: {e}")
            target_city = None

    if detected_lat is not None and detected_lon is not None:
        url = f"https://wttr.in/{detected_lat:.4f},{detected_lon:.4f}?format=j1"
    elif target_city:
        encoded_city = quote_plus(target_city)
        url = f"https://wttr.in/{encoded_city}?format=j1"
    else:
        url = "https://wttr.in/?format=j1"

    fallback = {
        "status": "unavailable",
        "city": target_city or "Local Area",
        "temp_c": 26,
        "condition": "Clear",
        "humidity": "65%",
        "wind": "10 km/h",
        "feels_like": 26,
        "summary": "Weather telemetry temporarily offline.",
    }

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "curl/7.68.0"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            current = data.get("current_condition", [{}])[0]
            nearest = data.get("nearest_area", [{}])[0]

            detected_city = target_city
            if not detected_city:
                area_names = nearest.get("areaName", [{}])
                detected_city = area_names[0].get("value") if area_names else "Current Location"

            temp_c = int(current.get("temp_C", 26))
            desc = _cond_pt(current.get("weatherDesc", [{}])[0].get("value", "Clear"))
            humidity = f"{current.get('humidity', '60')}%"
            wind_speed = f"{current.get('windspeedKmph', '10')} km/h"
            feels_like = int(current.get("FeelsLikeC", temp_c))

            return {
                "status": "success",
                "city": detected_city,
                "temp_c": temp_c,
                "condition": desc,
                "humidity": humidity,
                "wind": wind_speed,
                "feels_like": feels_like,
                "summary": f"{temp_c}°C, {desc} em {detected_city}",
            }
    except Exception as e:
        print(f"[Weather] Live weather fetch notice: {e}")
        return fallback


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None
):
    """
    Weather report action.
    Fetches real-time live weather metrics and optionally opens Google Weather.
    """
    city = parameters.get("city") if parameters else None
    time_param = parameters.get("time", "today") if parameters else "today"

    weather = get_live_weather(city)
    city_name = weather.get("city", "sua região")
    temp = weather.get("temp_c", 26)
    cond = weather.get("condition", "céu limpo")

    msg = f"A previsão em {city_name} está {temp} graus Celsius, com {cond}."
    _speak_and_log(msg, player)

    # Optional browser fallback if user explicitly asks or city was specified
    search_query = f"weather in {city_name} {time_param}"
    if parameters and parameters.get("open_browser", False):
        try:
            encoded_query = quote_plus(search_query)
            webbrowser.open(f"https://www.google.com/search?q={encoded_query}")
        except Exception:
            pass

    if session_memory:
        try:
            session_memory.set_last_search(query=search_query, response=msg)
        except Exception:
            pass

    return msg


def _speak_and_log(message: str, player=None):
    # Intentionally does NOT write to the chat: the tool returns the text and the
    # live model speaks it, which is what gets transcribed into the chat. Logging
    # here as well would show the same line twice.
    return