"""
=============================================================
  🌤️  WeatherPulse — Advanced GUI Weather App
  Author  : Internship Project (Advanced Level)
  Stack   : Python 3 · Tkinter · Open-Meteo API (free, no key needed)
            + ip-api.com for GPS auto-detection
  Run     : python weather_app.py
  Deps    : requests  →  pip install requests
=============================================================
Features
--------
✅ Modern dark-themed Tkinter GUI (no extra libs needed)
✅ Location input  OR  automatic GPS detection via IP
✅ Current conditions (temp, feels-like, humidity, wind, UV, pressure)
✅ Hourly forecast  (next 12 hours)  with animated scrollable cards
✅ 7-day daily forecast strip
✅ Weather icons via Unicode emoji  (no image files needed)
✅ °C / °F  toggle with live conversion
✅ Wind speed  km/h / mph  toggle
✅ Full error handling with user-friendly messages
✅ Refresh button + auto-refresh every 10 minutes
✅ Responsive canvas with scrollbar for hourly data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import math
from datetime import datetime, timedelta
import threading
import time

# ──────────────────────────────────────────────────────────────
#  THEME / COLOUR PALETTE
# ──────────────────────────────────────────────────────────────
COLORS = {
    "bg":         "#0D1117",   # deep navy-black background
    "card":       "#161B22",   # card background
    "card2":      "#1C2333",   # secondary card / hover
    "accent":     "#58A6FF",   # sky-blue accent
    "accent2":    "#1F6FEB",   # darker accent for gradients
    "text":       "#E6EDF3",   # primary text
    "subtext":    "#8B949E",   # secondary / muted text
    "good":       "#3FB950",   # green — good conditions
    "warn":       "#D29922",   # amber — moderate
    "danger":     "#F85149",   # red — severe
    "border":     "#30363D",   # subtle border
    "hourly_bg":  "#1A2332",   # hourly card face
}

FONTS = {
    "hero":    ("Segoe UI", 64, "bold"),
    "h1":      ("Segoe UI", 22, "bold"),
    "h2":      ("Segoe UI", 15, "bold"),
    "h3":      ("Segoe UI", 12, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 9),
    "mono":    ("Consolas", 10),
    "icon":    ("Segoe UI Emoji", 28),
    "icon_sm": ("Segoe UI Emoji", 18),
}

# ──────────────────────────────────────────────────────────────
#  WEATHER CODE → DESCRIPTION + EMOJI
# ──────────────────────────────────────────────────────────────
WMO_CODES = {
    0:  ("Clear sky",              "☀️"),
    1:  ("Mainly clear",           "🌤️"),
    2:  ("Partly cloudy",          "⛅"),
    3:  ("Overcast",               "☁️"),
    45: ("Foggy",                  "🌫️"),
    48: ("Icy fog",                "🌫️"),
    51: ("Light drizzle",          "🌦️"),
    53: ("Drizzle",                "🌦️"),
    55: ("Heavy drizzle",          "🌧️"),
    56: ("Freezing drizzle",       "🌨️"),
    57: ("Heavy freezing drizzle", "🌨️"),
    61: ("Slight rain",            "🌧️"),
    63: ("Rain",                   "🌧️"),
    65: ("Heavy rain",             "🌧️"),
    66: ("Freezing rain",          "🌨️"),
    67: ("Heavy freezing rain",    "🌨️"),
    71: ("Slight snow",            "🌨️"),
    73: ("Snow",                   "❄️"),
    75: ("Heavy snow",             "❄️"),
    77: ("Snow grains",            "🌨️"),
    80: ("Slight showers",         "🌦️"),
    81: ("Showers",                "🌦️"),
    82: ("Violent showers",        "⛈️"),
    85: ("Snow showers",           "🌨️"),
    86: ("Heavy snow showers",     "❄️"),
    95: ("Thunderstorm",           "⛈️"),
    96: ("Thunderstorm + hail",    "⛈️"),
    99: ("Thunderstorm + hail",    "⛈️"),
}

def wmo_info(code):
    return WMO_CODES.get(code, ("Unknown", "🌡️"))

# ──────────────────────────────────────────────────────────────
#  API HELPERS
# ──────────────────────────────────────────────────────────────

class WeatherAPI:
    """Wraps Open-Meteo (free, no API key) + geocoding."""

    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    IP_GEO_URL  = "http://ip-api.com/json/"

    @staticmethod
    def get_location_by_ip():
        """Auto-detect location via IP geolocation."""
        try:
            r = requests.get(WeatherAPI.IP_GEO_URL, timeout=5)
            r.raise_for_status()
            d = r.json()
            if d.get("status") == "success":
                return {
                    "name": f"{d['city']}, {d['country']}",
                    "lat":  d["lat"],
                    "lon":  d["lon"],
                }
        except Exception:
            pass
        return None

    @staticmethod
    def geocode(city: str):
        """Return (name, lat, lon) for a city name string."""
        try:
            r = requests.get(
                WeatherAPI.GEOCODE_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=6,
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            if not results:
                return None
            loc = results[0]
            parts = [loc["name"]]
            if loc.get("admin1"):
                parts.append(loc["admin1"])
            if loc.get("country"):
                parts.append(loc["country"])
            return {
                "name": ", ".join(parts),
                "lat":  loc["latitude"],
                "lon":  loc["longitude"],
            }
        except Exception as e:
            raise RuntimeError(f"Geocoding failed: {e}")

    @staticmethod
    def fetch_weather(lat: float, lon: float):
        """Fetch full forecast from Open-Meteo."""
        params = {
            "latitude":  lat,
            "longitude": lon,
            "current": [
                "temperature_2m", "apparent_temperature", "relative_humidity_2m",
                "precipitation", "weather_code", "surface_pressure",
                "wind_speed_10m", "wind_direction_10m", "uv_index", "is_day",
            ],
            "hourly": [
                "temperature_2m", "apparent_temperature", "relative_humidity_2m",
                "precipitation_probability", "weather_code", "wind_speed_10m",
            ],
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "wind_speed_10m_max", "uv_index_max",
                "sunrise", "sunset",
            ],
            "wind_speed_unit":   "kmh",
            "timezone":          "auto",
            "forecast_days":     7,
        }
        try:
            r = requests.get(WeatherAPI.WEATHER_URL, params=params, timeout=8)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise RuntimeError(f"Weather fetch failed: {e}")


# ──────────────────────────────────────────────────────────────
#  UNIT CONVERSION HELPERS
# ──────────────────────────────────────────────────────────────

def c_to_f(c):
    return c * 9 / 5 + 32

def kmh_to_mph(k):
    return k * 0.621371

def fmt_temp(c, unit="C"):
    val = c if unit == "C" else c_to_f(c)
    return f"{val:.0f}°{unit}"

def fmt_wind(kmh, unit="kmh"):
    if unit == "mph":
        return f"{kmh_to_mph(kmh):.1f} mph"
    return f"{kmh:.1f} km/h"

def wind_direction_arrow(deg):
    arrows = ["N","NE","E","SE","S","SW","W","NW"]
    idx = round(deg / 45) % 8
    return arrows[idx]

def uv_label(uv):
    if uv < 3:  return ("Low",       COLORS["good"])
    if uv < 6:  return ("Moderate",  COLORS["warn"])
    if uv < 8:  return ("High",      COLORS["warn"])
    if uv < 11: return ("Very High", COLORS["danger"])
    return              ("Extreme",  COLORS["danger"])


# ──────────────────────────────────────────────────────────────
#  ROUNDED RECTANGLE HELPER
# ──────────────────────────────────────────────────────────────

def rounded_rect(canvas, x1, y1, x2, y2, r=12, **kw):
    """Draw a rounded rectangle on a canvas."""
    pts = [
        x1+r, y1,   x2-r, y1,
        x2, y1,     x2, y1+r,
        x2, y2-r,   x2, y2,
        x2-r, y2,   x1+r, y2,
        x1, y2,     x1, y2-r,
        x1, y1+r,   x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


# ──────────────────────────────────────────────────────────────
#  TOOLTIP
# ──────────────────────────────────────────────────────────────

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0,0,0,0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text, bg="#2D333B", fg=COLORS["text"],
                       font=FONTS["small"], relief="flat", padx=6, pady=3)
        lbl.pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ──────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ──────────────────────────────────────────────────────────────

class WeatherApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("WeatherPulse")
        self.geometry("980x780")
        self.minsize(800, 680)
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        # State
        self._unit_temp  = tk.StringVar(value="C")
        self._unit_wind  = tk.StringVar(value="kmh")
        self._weather    = None      # raw API response
        self._location   = None      # {name, lat, lon}
        self._last_fetch = None
        self._auto_job   = None

        self._build_ui()
        self._auto_detect_location()

    # ── UI CONSTRUCTION ────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_search_bar()
        self._build_main_content()
        self._build_status_bar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg"])
        hdr.pack(fill="x", padx=20, pady=(16, 0))

        logo = tk.Label(hdr, text="🌤️  WeatherPulse",
                        font=("Segoe UI", 20, "bold"),
                        fg=COLORS["accent"], bg=COLORS["bg"])
        logo.pack(side="left")

        # Unit toggles (right side)
        toggle_frame = tk.Frame(hdr, bg=COLORS["bg"])
        toggle_frame.pack(side="right")

        tk.Label(toggle_frame, text="Temp:", font=FONTS["small"],
                 fg=COLORS["subtext"], bg=COLORS["bg"]).pack(side="left", padx=(0,4))
        for unit in ("C", "F"):
            rb = tk.Radiobutton(toggle_frame, text=f"°{unit}",
                                variable=self._unit_temp, value=unit,
                                command=self._on_unit_change,
                                font=FONTS["body"], fg=COLORS["text"],
                                bg=COLORS["bg"], activebackground=COLORS["bg"],
                                selectcolor=COLORS["card2"],
                                relief="flat", indicatoron=False,
                                padx=8, pady=3, bd=0,
                                highlightthickness=0)
            rb.pack(side="left", padx=2)

        tk.Label(toggle_frame, text="  Wind:", font=FONTS["small"],
                 fg=COLORS["subtext"], bg=COLORS["bg"]).pack(side="left", padx=(8,4))
        for wunit, wlabel in (("kmh","km/h"), ("mph","mph")):
            rb = tk.Radiobutton(toggle_frame, text=wlabel,
                                variable=self._unit_wind, value=wunit,
                                command=self._on_unit_change,
                                font=FONTS["body"], fg=COLORS["text"],
                                bg=COLORS["bg"], activebackground=COLORS["bg"],
                                selectcolor=COLORS["card2"],
                                relief="flat", indicatoron=False,
                                padx=8, pady=3, bd=0,
                                highlightthickness=0)
            rb.pack(side="left", padx=2)

    def _build_search_bar(self):
        bar = tk.Frame(self, bg=COLORS["bg"])
        bar.pack(fill="x", padx=20, pady=(12, 0))

        # Entry
        entry_frame = tk.Frame(bar, bg=COLORS["border"], bd=0)
        entry_frame.pack(side="left", fill="x", expand=True)

        self._search_var = tk.StringVar()
        self._entry = tk.Entry(entry_frame, textvariable=self._search_var,
                               font=FONTS["h2"], bg=COLORS["card"],
                               fg=COLORS["text"], insertbackground=COLORS["accent"],
                               relief="flat", bd=0)
        self._entry.pack(fill="both", expand=True, ipady=10, ipadx=14)
        self._entry.bind("<Return>", lambda e: self._on_search())
        self._entry.insert(0, "Enter city name…")
        self._entry.bind("<FocusIn>",  self._clear_placeholder)
        self._entry.bind("<FocusOut>", self._restore_placeholder)

        # Buttons
        for label, cmd, tip in (
            ("🔍 Search",  self._on_search,          "Search for a city"),
            ("📍 Auto",    self._auto_detect_location,"Detect via IP location"),
            ("🔄 Refresh", self._refresh,             "Refresh weather data"),
        ):
            btn = tk.Button(bar, text=label, command=cmd,
                            font=FONTS["body"], bg=COLORS["accent2"],
                            fg="white", activebackground=COLORS["accent"],
                            activeforeground="white", relief="flat",
                            cursor="hand2", padx=14, pady=8, bd=0)
            btn.pack(side="left", padx=(8, 0))
            ToolTip(btn, tip)

    def _build_main_content(self):
        # Scrollable main area
        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True, padx=0, pady=8)

        canvas = tk.Canvas(container, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._main_canvas = canvas
        self._scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self._scroll_win = canvas.create_window((0, 0), window=self._scroll_frame,
                                                anchor="nw")

        self._scroll_frame.bind("<Configure>", self._on_frame_configure)
        canvas.bind("<Configure>", self._on_canvas_configure)
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Placeholder
        self._placeholder_lbl = tk.Label(
            self._scroll_frame,
            text="🌍\n\nEnter a city name above\nor click 📍 Auto to detect your location",
            font=FONTS["h2"], fg=COLORS["subtext"], bg=COLORS["bg"],
            justify="center"
        )
        self._placeholder_lbl.pack(expand=True, pady=120)

    def _build_status_bar(self):
        self._status_var = tk.StringVar(value="Ready")
        status = tk.Label(self, textvariable=self._status_var,
                          font=FONTS["small"], fg=COLORS["subtext"],
                          bg=COLORS["card"], anchor="w", padx=12, pady=4)
        status.pack(fill="x", side="bottom")

    # ── SCROLL HELPERS ─────────────────────────────────────────

    def _on_frame_configure(self, event=None):
        self._main_canvas.configure(
            scrollregion=self._main_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._main_canvas.itemconfig(self._scroll_win, width=event.width)

    def _on_mousewheel(self, event):
        self._main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── ENTRY PLACEHOLDER ──────────────────────────────────────

    def _clear_placeholder(self, event):
        if self._search_var.get() == "Enter city name…":
            self._entry.delete(0, "end")
            self._entry.config(fg=COLORS["text"])

    def _restore_placeholder(self, event):
        if not self._search_var.get().strip():
            self._entry.insert(0, "Enter city name…")
            self._entry.config(fg=COLORS["subtext"])

    # ── ACTIONS ────────────────────────────────────────────────

    def _set_status(self, msg, color=None):
        self._status_var.set(msg)
        # brief flash for long messages
        self.update_idletasks()

    def _on_search(self):
        city = self._search_var.get().strip()
        if not city or city == "Enter city name…":
            messagebox.showwarning("Input Required", "Please type a city name first.")
            return
        self._fetch_for_city(city)

    def _auto_detect_location(self):
        self._set_status("📍 Detecting location via IP…")
        def task():
            loc = WeatherAPI.get_location_by_ip()
            if loc:
                self.after(0, lambda: self._load_weather(loc))
            else:
                self.after(0, lambda: self._set_status(
                    "⚠️  Auto-detect failed — please type a city name"))
        threading.Thread(target=task, daemon=True).start()

    def _fetch_for_city(self, city: str):
        self._set_status(f"Searching for '{city}'...")
        def task():
            try:
                loc = WeatherAPI.geocode(city)
                if not loc:
                    self.after(0, lambda: self._show_error(
                        f"City '{city}' not found. Check spelling and try again."))
                    return
                self.after(0, lambda: self._load_weather(loc))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
        threading.Thread(target=task, daemon=True).start()

    def _refresh(self):
        if not self._location:
            messagebox.showinfo("No Location", "Search for a location first.")
            return
        self._load_weather(self._location)

    def _load_weather(self, loc: dict):
        self._location = loc
        city_name = loc["name"]
        self._set_status(f"☁️  Fetching weather for {city_name}…")

        def task():
            try:
                data = WeatherAPI.fetch_weather(loc["lat"], loc["lon"])
                self.after(0, lambda: self._render(data, city_name))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
        threading.Thread(target=task, daemon=True).start()

    def _on_unit_change(self):
        if self._weather:
            city = self._location["name"] if self._location else "Unknown"
            self._render(self._weather, city)

    def _show_error(self, msg: str):
        self._set_status(f"❌ Error — {msg}")
        messagebox.showerror("WeatherPulse Error",
                             f"{msg}\n\nCheck your internet connection and try again.")

    # ── RENDER ─────────────────────────────────────────────────

    def _render(self, data: dict, city_name: str):
        self._weather = data

        # Clear existing content
        for w in self._scroll_frame.winfo_children():
            w.destroy()

        unit_t = self._unit_temp.get()
        unit_w = self._unit_wind.get()

        cur = data["current"]
        hrly = data["hourly"]
        daily = data["daily"]
        tz_offset = data.get("utc_offset_seconds", 0)

        # ── CURRENT CONDITIONS ────────────────────────────────
        self._render_current(cur, city_name, unit_t, unit_w)

        # ── DETAIL STATS GRID ─────────────────────────────────
        self._render_stats(cur, unit_w)

        # ── HOURLY FORECAST ───────────────────────────────────
        self._render_hourly(hrly, unit_t, tz_offset)

        # ── 7-DAY FORECAST ────────────────────────────────────
        self._render_daily(daily, unit_t)

        # ── SUNRISE / SUNSET ──────────────────────────────────
        self._render_sun(daily)

        ts = datetime.now().strftime("%H:%M:%S")
        self._set_status(f"✅ Updated at {ts}  |  {city_name}")
        self._last_fetch = time.time()
        self._schedule_auto_refresh()

    def _section_label(self, parent, text):
        frm = tk.Frame(parent, bg=COLORS["bg"])
        frm.pack(fill="x", padx=20, pady=(16, 6))
        tk.Label(frm, text=text, font=FONTS["h2"],
                 fg=COLORS["accent"], bg=COLORS["bg"]).pack(side="left")
        tk.Frame(frm, bg=COLORS["border"], height=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0), pady=8)

    def _render_current(self, cur, city_name, unit_t, unit_w):
        card = tk.Frame(self._scroll_frame, bg=COLORS["card"],
                        bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"])
        card.pack(fill="x", padx=20, pady=(8, 0))

        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        code = cur.get("weather_code", 0)
        desc, icon = wmo_info(code)
        temp_c = cur.get("temperature_2m", 0)
        feels_c = cur.get("apparent_temperature", 0)

        # LEFT: icon + temp
        left = tk.Frame(inner, bg=COLORS["card"])
        left.pack(side="left", padx=(0, 30))

        tk.Label(left, text=icon, font=("Segoe UI Emoji", 72),
                 bg=COLORS["card"]).pack()
        tk.Label(left, text=fmt_temp(temp_c, unit_t),
                 font=("Segoe UI", 58, "bold"),
                 fg=COLORS["text"], bg=COLORS["card"]).pack()
        tk.Label(left, text=f"Feels like {fmt_temp(feels_c, unit_t)}",
                 font=FONTS["body"], fg=COLORS["subtext"], bg=COLORS["card"]).pack()

        # RIGHT: city + description + quick stats
        right = tk.Frame(inner, bg=COLORS["card"])
        right.pack(side="left", fill="both", expand=True, anchor="n")

        tk.Label(right, text=city_name, font=FONTS["h1"],
                 fg=COLORS["text"], bg=COLORS["card"],
                 wraplength=450, justify="left").pack(anchor="w")
        tk.Label(right, text=desc, font=FONTS["h2"],
                 fg=COLORS["subtext"], bg=COLORS["card"]).pack(anchor="w", pady=(4, 16))

        quick = tk.Frame(right, bg=COLORS["card"])
        quick.pack(anchor="w")

        wind_spd = cur.get("wind_speed_10m", 0)
        wind_dir = cur.get("wind_direction_10m", 0)
        humidity = cur.get("relative_humidity_2m", 0)
        precip   = cur.get("precipitation", 0)

        quick_items = [
            ("💨", f"{fmt_wind(wind_spd, unit_w)}  {wind_direction_arrow(wind_dir)}",
             "Wind speed & direction"),
            ("💧", f"{humidity}%",   "Relative humidity"),
            ("🌧️", f"{precip:.1f} mm", "Current precipitation"),
        ]
        for emoji, val, tip in quick_items:
            f = tk.Frame(quick, bg=COLORS["card2"], padx=10, pady=6)
            f.pack(side="left", padx=(0, 10), pady=4)
            tk.Label(f, text=emoji, font=FONTS["icon_sm"],
                     bg=COLORS["card2"]).pack(side="left", padx=(0, 6))
            tk.Label(f, text=val, font=FONTS["h3"],
                     fg=COLORS["text"], bg=COLORS["card2"]).pack(side="left")
            ToolTip(f, tip)

        is_day = cur.get("is_day", 1)
        day_lbl = tk.Label(right, text="🌞 Daytime" if is_day else "🌙 Nighttime",
                           font=FONTS["small"], fg=COLORS["subtext"],
                           bg=COLORS["card"])
        day_lbl.pack(anchor="w", pady=(12, 0))

    def _render_stats(self, cur, unit_w):
        self._section_label(self._scroll_frame, "📊 Current Conditions")

        grid_frame = tk.Frame(self._scroll_frame, bg=COLORS["bg"])
        grid_frame.pack(fill="x", padx=20)

        uv = cur.get("uv_index", 0)
        uv_lbl, uv_color = uv_label(uv)
        pressure = cur.get("surface_pressure", 0)
        wind_spd = cur.get("wind_speed_10m", 0)
        wind_dir = cur.get("wind_direction_10m", 0)

        items = [
            ("🌬️", "Wind Speed",  fmt_wind(wind_spd, unit_w), None),
            ("🧭", "Wind Dir.",   f"{wind_direction_arrow(wind_dir)} ({wind_dir:.0f}°)", None),
            ("🔆", "UV Index",    f"{uv:.1f}  {uv_lbl}", uv_color),
            ("🌡️", "Pressure",    f"{pressure:.0f} hPa", None),
            ("💧", "Humidity",    f"{cur.get('relative_humidity_2m', 0)}%", None),
            ("🌧️", "Precipitation", f"{cur.get('precipitation', 0):.1f} mm", None),
        ]

        for i, (emoji, label, value, color) in enumerate(items):
            cell = tk.Frame(grid_frame, bg=COLORS["card"],
                            bd=0, highlightthickness=1,
                            highlightbackground=COLORS["border"])
            cell.grid(row=i//3, column=i%3, padx=6, pady=6, sticky="nsew")
            grid_frame.columnconfigure(i%3, weight=1)

            tk.Label(cell, text=emoji, font=FONTS["icon_sm"],
                     bg=COLORS["card"]).pack(pady=(12, 2))
            tk.Label(cell, text=label, font=FONTS["small"],
                     fg=COLORS["subtext"], bg=COLORS["card"]).pack()
            tk.Label(cell, text=value, font=FONTS["h2"],
                     fg=color or COLORS["text"], bg=COLORS["card"]).pack(pady=(2, 12))

    def _render_hourly(self, hrly, unit_t, tz_offset):
        self._section_label(self._scroll_frame, "⏱️ Next 12 Hours")

        outer = tk.Frame(self._scroll_frame, bg=COLORS["bg"])
        outer.pack(fill="x", padx=20, pady=(0, 8))

        # Taller canvas so cards are never clipped
        h_canvas = tk.Canvas(outer, bg=COLORS["bg"],
                             height=190, highlightthickness=0)
        h_scroll = ttk.Scrollbar(outer, orient="horizontal",
                                 command=h_canvas.xview)
        h_canvas.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")
        h_canvas.pack(fill="x", expand=True)

        inner = tk.Frame(h_canvas, bg=COLORS["bg"])
        h_canvas.create_window((0, 0), window=inner, anchor="nw")

        # Open-Meteo returns times in the location local timezone already.
        # Compute local "now" by shifting UTC by tz_offset, then compare.
        times = hrly.get("time", [])
        local_now = datetime.utcnow() + timedelta(seconds=tz_offset)
        local_now_str = local_now.strftime("%Y-%m-%dT%H:00")

        start_idx = 0
        for i, t in enumerate(times):
            if t >= local_now_str:
                start_idx = i
                break

        temp_list   = hrly.get("temperature_2m", [])
        code_list   = hrly.get("weather_code", [])
        precip_list = hrly.get("precipitation_probability", [])

        cards_added = 0
        for offset in range(24):        # scan up to 24 slots to get 12 valid cards
            idx = start_idx + offset
            if idx >= len(times) or cards_added >= 12:
                break

            t_str = times[idx]
            try:
                dt = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
                hr_label = dt.strftime("%I %p").lstrip("0") or "12 AM"
                if offset == 0:
                    hr_label = "Now"
            except Exception:
                hr_label = t_str[-5:]

            temp_c = temp_list[idx]   if idx < len(temp_list)   else 0
            code   = code_list[idx]   if idx < len(code_list)   else 0
            precip = precip_list[idx] if idx < len(precip_list) else 0
            _, icon = wmo_info(code)

            # Let the card size itself naturally — no pack_propagate(False)
            card = tk.Frame(inner, bg=COLORS["hourly_bg"],
                            bd=0, highlightthickness=1,
                            highlightbackground=COLORS["border"])
            card.pack(side="left", padx=5, pady=6, anchor="n")

            tk.Label(card, text=hr_label, font=FONTS["small"],
                     fg=COLORS["accent"] if offset == 0 else COLORS["subtext"],
                     bg=COLORS["hourly_bg"], width=7).pack(pady=(10, 0))
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 22),
                     bg=COLORS["hourly_bg"]).pack(pady=(4, 2))
            tk.Label(card, text=fmt_temp(temp_c, unit_t),
                     font=FONTS["h3"], fg=COLORS["text"],
                     bg=COLORS["hourly_bg"]).pack()
            tk.Label(card,
                     text=f"💧 {precip}%",
                     font=FONTS["small"],
                     fg=COLORS["accent"] if precip > 30 else COLORS["subtext"],
                     bg=COLORS["hourly_bg"]).pack(pady=(3, 10))

            cards_added += 1

        inner.update_idletasks()
        h_canvas.configure(scrollregion=h_canvas.bbox("all"))

        def _sync(event=None):
            inner.update_idletasks()
            h_canvas.configure(scrollregion=h_canvas.bbox("all"))
        inner.bind("<Configure>", _sync)

    def _render_daily(self, daily, unit_t):
        self._section_label(self._scroll_frame, "📅 7-Day Forecast")

        day_frame = tk.Frame(self._scroll_frame, bg=COLORS["bg"])
        day_frame.pack(fill="x", padx=20)

        times    = daily.get("time", [])
        codes    = daily.get("weather_code", [])
        t_max    = daily.get("temperature_2m_max", [])
        t_min    = daily.get("temperature_2m_min", [])
        precips  = daily.get("precipitation_sum", [])
        uv_maxes = daily.get("uv_index_max", [])

        day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

        for i in range(min(7, len(times))):
            try:
                dt = datetime.strptime(times[i], "%Y-%m-%d")
                day_name = "Today" if i == 0 else dt.strftime("%a")
                date_str = dt.strftime("%b %d")
            except Exception:
                day_name = f"Day {i+1}"
                date_str = ""

            code    = codes[i] if i < len(codes) else 0
            mx      = t_max[i] if i < len(t_max) else 0
            mn      = t_min[i] if i < len(t_min) else 0
            precip  = precips[i] if i < len(precips) else 0
            uv      = uv_maxes[i] if i < len(uv_maxes) else 0
            desc, icon = wmo_info(code)

            card = tk.Frame(day_frame, bg=COLORS["card"],
                            bd=0, highlightthickness=1,
                            highlightbackground=COLORS["border"])
            card.grid(row=0, column=i, padx=5, pady=4, sticky="nsew")
            day_frame.columnconfigure(i, weight=1)

            tk.Label(card, text=day_name, font=FONTS["h3"],
                     fg=COLORS["text"], bg=COLORS["card"]).pack(pady=(10, 0))
            tk.Label(card, text=date_str, font=FONTS["small"],
                     fg=COLORS["subtext"], bg=COLORS["card"]).pack()
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 24),
                     bg=COLORS["card"]).pack(pady=6)
            tk.Label(card, text=fmt_temp(mx, unit_t),
                     font=FONTS["h3"], fg=COLORS["text"],
                     bg=COLORS["card"]).pack()
            tk.Label(card, text=fmt_temp(mn, unit_t),
                     font=FONTS["small"], fg=COLORS["subtext"],
                     bg=COLORS["card"]).pack()

            uv_lbl, uv_clr = uv_label(uv)
            tk.Label(card, text=f"UV {uv:.0f}",
                     font=FONTS["small"], fg=uv_clr,
                     bg=COLORS["card"]).pack(pady=(4, 2))
            tk.Label(card, text=f"🌧️{precip:.1f}mm",
                     font=FONTS["small"], fg=COLORS["subtext"],
                     bg=COLORS["card"]).pack(pady=(0, 10))

    def _render_sun(self, daily):
        if not daily.get("sunrise") or not daily.get("sunset"):
            return

        self._section_label(self._scroll_frame, "🌅 Sunrise & Sunset")
        row = tk.Frame(self._scroll_frame, bg=COLORS["bg"])
        row.pack(fill="x", padx=20, pady=(0, 20))

        try:
            rise_str = daily["sunrise"][0]
            set_str  = daily["sunset"][0]
            rise_dt  = datetime.fromisoformat(rise_str)
            set_dt   = datetime.fromisoformat(set_str)
            day_len  = set_dt - rise_dt
            hours, rem = divmod(int(day_len.total_seconds()), 3600)
            mins = rem // 60
        except Exception:
            rise_str = set_str = "N/A"
            hours = mins = 0

        for label, icon, time_str in (
            ("Sunrise", "🌅", rise_dt.strftime("%I:%M %p") if isinstance(rise_dt, datetime) else "N/A"),
            ("Sunset",  "🌇", set_dt.strftime("%I:%M %p")  if isinstance(set_dt, datetime)  else "N/A"),
        ):
            card = tk.Frame(row, bg=COLORS["card"],
                            bd=0, highlightthickness=1,
                            highlightbackground=COLORS["border"])
            card.pack(side="left", expand=True, fill="both", padx=(0, 8), pady=4)

            tk.Label(card, text=icon, font=("Segoe UI Emoji", 30),
                     bg=COLORS["card"]).pack(pady=(12, 4))
            tk.Label(card, text=time_str, font=FONTS["h2"],
                     fg=COLORS["text"], bg=COLORS["card"]).pack()
            tk.Label(card, text=label, font=FONTS["small"],
                     fg=COLORS["subtext"], bg=COLORS["card"]).pack(pady=(2, 12))

        # Daylight duration
        dur_card = tk.Frame(row, bg=COLORS["card"],
                            bd=0, highlightthickness=1,
                            highlightbackground=COLORS["border"])
        dur_card.pack(side="left", expand=True, fill="both", padx=(0, 0), pady=4)
        tk.Label(dur_card, text="⏳", font=("Segoe UI Emoji", 30),
                 bg=COLORS["card"]).pack(pady=(12, 4))
        tk.Label(dur_card, text=f"{hours}h {mins}m", font=FONTS["h2"],
                 fg=COLORS["text"], bg=COLORS["card"]).pack()
        tk.Label(dur_card, text="Daylight", font=FONTS["small"],
                 fg=COLORS["subtext"], bg=COLORS["card"]).pack(pady=(2, 12))

    # ── AUTO REFRESH ───────────────────────────────────────────

    def _schedule_auto_refresh(self):
        if self._auto_job:
            self.after_cancel(self._auto_job)
        # Auto-refresh every 10 minutes
        self._auto_job = self.after(600_000, self._refresh)


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()