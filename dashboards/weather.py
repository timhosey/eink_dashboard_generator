import os
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo

WEATHER_CODE_MAP = {
    0: "sunny",
    1: "sunny-overcast",
    2: "cloudy",
    3: "cloudy",
    45: "fog",
    48: "fog",
    51: "sprinkle",
    53: "showers",
    55: "storm-showers",
    56: "sleet",
    57: "sleet-storm",
    61: "rain-mix",
    63: "rain",
    65: "rain-wind",
    71: "snow",
    73: "snow",
    75: "snow-wind",
    80: "showers",
    81: "rain",
    82: "rain-wind",
    85: "snow",
    86: "snow-wind",
    95: "thunderstorm",
    96: "hail",
    99: "hail"
}


# Helper to fetch and parse current weather from Open-Meteo
def get_weather(zip_code="94103"):
    try:
        # Use Open-Meteo's geocoding API to get lat/lon from zip
        geo_resp = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1", timeout=5)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()["results"][0]
        lat = geo_data["latitude"]
        lon = geo_data["longitude"]
        location = f"{geo_data['name']}, {geo_data.get('admin1', '')}, {geo_data.get('country', '')}".strip(', ')

        # Now fetch weather data with daily forecast and sunrise/sunset
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset"
            f"&timezone={geo_data.get('timezone', 'auto')}"
        )
        weather_resp = requests.get(url, timeout=5)
        weather_resp.raise_for_status()
        data = weather_resp.json()
        current = data.get("current_weather", {})
        daily = data.get("daily", {})

        forecast = []
        days = daily
        for i in range(min(5, len(days.get("time", [])))):
            date = days["time"][i]
            high = int((days["temperature_2m_max"][i] * 9/5) + 32)
            low = int((days["temperature_2m_min"][i] * 9/5) + 32)
            code = days["weathercode"][i]
            icon = WEATHER_CODE_MAP.get(code, "na")
            sunrise = days["sunrise"][i] if "sunrise" in days and i < len(days["sunrise"]) else ""
            sunset = days["sunset"][i] if "sunset" in days and i < len(days["sunset"]) else ""
            forecast.append({"date": date, "high": high, "low": low, "icon": icon, "sunrise": sunrise, "sunset": sunset, "code": code})

        return {
            "temp": f"{int((current.get('temperature', 0) * 9/5) + 32)}°F",
            "desc": "Cloudy" if current.get("cloudcover", 0) > 50 else "Clear",
            "icon": WEATHER_CODE_MAP.get(current.get("weathercode", 0), "na"),
            "location": location,
            "timezone": geo_data.get("timezone", "UTC"),
            "forecast": forecast
        }
    except Exception:
        return {
            "temp": "N/A",
            "desc": "Unavailable",
            "icon": "wi-na.png",
            "location": "Unknown",
            "timezone": "UTC",
            "forecast": []
        }

def render():
    img = Image.new('L', (600, 800), color=255)  # 'L' = 8-bit grayscale
    draw = ImageDraw.Draw(img)

    # Get current weather
    weather = get_weather("98405")

    is_night = False
    if weather["forecast"]:
        sunrise = weather["forecast"][0].get("sunrise")
        sunset = weather["forecast"][0].get("sunset")
        try:
            local_time = datetime.now(ZoneInfo(weather.get("timezone", "UTC")))
            sr = datetime.fromisoformat(sunrise).astimezone(ZoneInfo(weather.get("timezone", "UTC")))
            ss = datetime.fromisoformat(sunset).astimezone(ZoneInfo(weather.get("timezone", "UTC")))
            is_night = not (sr <= local_time <= ss)
        except Exception:
            pass

    # Adjust icon for night-specific overrides
    main_icon_key = weather['icon']
    if is_night:
        if main_icon_key in ["clear", "sunny", "sunny-overcast"]:
            main_icon_key = "clear"
    icon_prefix = "wi-night" if is_night else "wi-day"
    icon_filename = f"{icon_prefix}-{main_icon_key}.png"
    icon_path = os.path.join(os.path.dirname(__file__), f"../icons/{icon_filename}")
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((100, 100))
        flat_icon = Image.new("RGBA", icon.size, (255, 255, 255, 255))
        flat_icon.paste(icon, mask=icon.split()[3])
        gray_icon = flat_icon.convert("L")
        img.paste(gray_icon, (20, 150))

    # Load fonts
    font_path = 'fonts/CreatoDisplay-Regular.otf'
    font_huge = ImageFont.truetype(font_path, 52)
    font_large = ImageFont.truetype(font_path, 42)
    font_medium = ImageFont.truetype(font_path, 28)
    font_small = ImageFont.truetype(font_path, 20)
    font_tiny = ImageFont.truetype(font_path, 14)

    # Header
    draw.text((20, 30), "Weather", fill=0, font=font_huge)

    # Temperature and conditions
    draw.text((140, 155), f"{weather['temp']}", fill=0, font=font_large)
    draw.text((140, 205), f"{weather['desc']}", fill=0, font=font_medium)
    if weather["forecast"]:
        draw.text((260, 200), f"High: {weather['forecast'][0]['high']}°F", fill=0, font=font_tiny)
        draw.text((260, 220), f"Low: {weather['forecast'][0]['low']}°F", fill=0, font=font_tiny)

        sunrise_time = weather["forecast"][0].get("sunrise", "")[-5:]
        sunset_time = weather["forecast"][0].get("sunset", "")[-5:]

        icon_path_rise = os.path.join(os.path.dirname(__file__), "../icons/wi-sunrise.png")
        icon_path_set = os.path.join(os.path.dirname(__file__), "../icons/wi-sunset.png")

        if os.path.exists(icon_path_rise):
            icon = Image.open(icon_path_rise).convert("RGBA").resize((20, 20))
            flat_icon = Image.new("RGBA", icon.size, (255, 255, 255, 255))
            flat_icon.paste(icon, mask=icon.split()[3])
            gray_icon = flat_icon.convert("L")
            img.paste(gray_icon, (260, 160))
        draw.text((280, 160), sunrise_time, fill=0, font=font_tiny)

        if os.path.exists(icon_path_set):
            icon = Image.open(icon_path_set).convert("RGBA").resize((20, 20))
            flat_icon = Image.new("RGBA", icon.size, (255, 255, 255, 255))
            flat_icon.paste(icon, mask=icon.split()[3])
            gray_icon = flat_icon.convert("L")
            img.paste(gray_icon, (260, 180))
        draw.text((280, 180), sunset_time, fill=0, font=font_tiny)

    # Draw 5-day forecast centered
    forecast_width = 5 * 100
    start_x = (600 - forecast_width) // 2

    for i, day in enumerate(weather["forecast"]):
        x = start_x + i * 110
        day_icon_key = day["icon"]
        if is_night and day_icon_key in ["sunny", "sunny-overcast"]:
            day_icon_key = "clear"
        day_icon_prefix = "wi-night" if is_night else "wi-day"
        # print(f"icon: {day_icon_key}")
        icon_path = os.path.join(os.path.dirname(__file__), f"../icons/{day_icon_prefix}-{day_icon_key}.png")
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("RGBA").resize((48, 48))
            flat_icon = Image.new("RGBA", icon.size, (255, 255, 255, 255))
            flat_icon.paste(icon, mask=icon.split()[3])
            gray_icon = flat_icon.convert("L")
            img.paste(gray_icon, (x, 340))
        draw.text((x, 300), day["date"][5:], fill=0, font=font_small)
        draw.text((x, 400), f"H: {day['high']}", fill=0, font=font_small)
        draw.text((x, 420), f"L: {day['low']}", fill=0, font=font_small)

        # Draw vertical divider lines between days
        if i < len(weather["forecast"]) - 1:
            divider_x = x + 85
            draw.line([(divider_x, 290), (divider_x, 460)], fill=128)

    # Location and timestamp
    draw.text((20, 720), f"Location: {weather['location']}", fill=0, font=font_small)
    local_time = datetime.now(ZoneInfo(weather.get("timezone", "UTC")))
    draw.text((20, 750), f"Updated: {local_time.strftime('%Y-%m-%d %H:%M')}", fill=128, font=font_small)

    output = '/tmp/weather.png'
    img.save(output, optimize=True)
    return output