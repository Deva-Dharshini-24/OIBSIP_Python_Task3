# 🌤️ WeatherPulse — Advanced Python Weather App

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green?style=for-the-badge)
![Open-Meteo](https://img.shields.io/badge/Open--Meteo-Free%20API-orange?style=for-the-badge&logo=cloud&logoColor=white)
![No API Key](https://img.shields.io/badge/API%20Key-Not%20Required-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A fully featured, dark-themed desktop weather application built with Python and Tkinter.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Tech Stack](#-tech-stack)

</div>

---

> **Intern Name:** Your Name Here
> **Task:** Task 2 — Python Development
> **Organization:** Oasis Infobyte (OIBSIP)
> **Submission Date:** June 2025

---

## 🎯 Overview

WeatherPulse is a feature-rich desktop weather app built entirely in Python using Tkinter. It fetches real-time weather data from the free Open-Meteo API — **no API key required** — and presents it in a clean, dark-themed GUI with current conditions, a 12-hour hourly forecast, a 7-day daily forecast, and unit conversion support. Location can be entered manually or auto-detected via IP geolocation.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📍 Auto GPS Detection | Detects your location automatically via IP geolocation |
| 🔍 City Search | Search any city worldwide with geocoding support |
| 🌡️ Current Conditions | Temperature, feels-like, humidity, precipitation, pressure |
| 💨 Wind Info | Wind speed + compass direction (N / NE / E …) |
| 🔆 UV Index | Color-coded UV severity (Low → Extreme) |
| ⏱️ 12-Hour Hourly Forecast | Scrollable cards with emoji icons + rain probability |
| 📅 7-Day Daily Forecast | High / low temps, UV index, precipitation per day |
| 🌅 Sunrise & Sunset | Rise time, set time, and total daylight duration |
| °C / °F Toggle | Live temperature unit conversion with one click |
| km/h / mph Toggle | Live wind speed unit conversion |
| 🔄 Auto Refresh | Weather data auto-refreshes every 10 minutes |
| 🌙 Dark Theme | Modern navy dark UI with accent colors |
| ⚡ Non-blocking UI | Background threads — UI never freezes during fetches |

---

## 🛠️ Tech Stack

| Tool / Library | Purpose |
|---|---|
| `Python 3.x` | Core language |
| `Tkinter` | Desktop GUI framework (built-in) |
| `requests` | HTTP calls to Open-Meteo and ip-api |
| `threading` | Background data fetching without UI freeze |
| `datetime` | Timestamp parsing and timezone offset handling |
| [Open-Meteo API](https://open-meteo.com/) | Free weather forecast data (no key needed) |
| [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api) | City name → latitude / longitude |
| [ip-api.com](http://ip-api.com/) | IP-based auto location detection |

---

## 📂 Project Structure

```
WeatherPulse/
│
├── weather_app.py       ← Main application (single file, fully self-contained)
├── requirements.txt     ← Python dependencies
├── README.md            ← Project documentation
├── .gitignore           ← Excludes cache and compiled files
└── assets/
    └── screenshot.png   ← App screenshot
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip
- Internet connection (for live weather data)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/WeatherPulse.git
cd WeatherPulse
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

> Tkinter comes built-in with Python on Windows and macOS.
> On Linux, install it with:
> ```bash
> sudo apt install python3-tk
> ```

### Step 3 — Run the Application

```bash
python weather_app.py
```

---

## 📖 Usage

1. **Auto Detect** — Click 📍 **Auto** to detect your location via IP and load weather instantly
2. **Search a City** — Type any city name in the search bar and press **Enter** or click 🔍 **Search**
3. **Switch Units** — Use the °C / °F and km/h / mph toggles in the top-right corner
4. **Refresh** — Click 🔄 **Refresh** to manually update, or wait 10 minutes for auto-refresh
5. **Scroll** — Scroll the hourly forecast row horizontally to see all 12 hours

---

## 🌐 APIs Used

| API | Base URL | Auth Required |
|---|---|---|
| Open-Meteo Forecast | `https://api.open-meteo.com/v1/forecast` | ❌ None |
| Open-Meteo Geocoding | `https://geocoding-api.open-meteo.com/v1/search` | ❌ None |
| ip-api Geolocation | `http://ip-api.com/json/` | ❌ None |

> 100% free APIs — no sign-up or API key needed at any stage.

---

## 📸 Screenshots

![WeatherPulse GUI](./assets/screenshot.png)

---

## 🎬 Demo

- 📺 YouTube Demo: [Insert YouTube Link Here]
- 💼 LinkedIn Post: [Insert LinkedIn Post Link Here]

---

## ⚠️ Limitations

- Weather data is sourced from Open-Meteo's free forecast model — accuracy may vary for very remote locations
- IP geolocation detects city-level location, not precise GPS coordinates
- Requires an active internet connection at all times

---

## 📝 File Naming Convention

As per OIBSIP guidelines: `YourName_Task2` — e.g., `RaviKumar_Task2`

---

## 📃 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Submitted as part of the **Oasis Infobyte Python Internship — OIBSIP** 🚀

⭐ If you found this useful, consider starring the repo!

</div>
