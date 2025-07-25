#!/usr/bin/env python3

from __future__ import annotations

# ── stdlib ──────────────────────────────────────────────────────────
import time
from typing import Final

# ── 3rd-party ───────────────────────────────────────────────────────
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastmcp import FastMCP

# ╔══════════════════════════════════════════════════════════════════╗
# 1.  Weather-code ➜ human-readable description lookup table         ║
# ╚══════════════════════════════════════════════════════════════════╝
# Open-Meteo returns the same “WMO weathercode” integers many APIs use.
WEATHER_CODES: Final[dict[int, str]] = {
    0:  "Clear sky",                     1:  "Mainly clear",
    2:  "Partly cloudy",                 3:  "Overcast",
    45: "Fog",                           48: "Depositing rime fog",
    51: "Light drizzle",                 53: "Moderate drizzle",
    55: "Dense drizzle",                 56: "Light freezing drizzle",
    57: "Dense freezing drizzle",        61: "Slight rain",
    63: "Moderate rain",                 65: "Heavy rain",
    66: "Light freezing rain",           67: "Heavy freezing rain",
    71: "Slight snow fall",              73: "Moderate snow fall",
    75: "Heavy snow fall",               77: "Snow grains",
    80: "Slight rain showers",           81: "Moderate rain showers",
    82: "Violent rain showers",          85: "Slight snow showers",
    86: "Heavy snow showers",            95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

# ╔══════════════════════════════════════════════════════════════════╗
# 2.  Build a requests.Session with automatic retries                ║
# ╚══════════════════════════════════════════════════════════════════╝
MAX_RETRIES    = 3       # total attempts = 1 original + 2 retries
BACKOFF_FACTOR = 1.5     # 1.5 s, then 2.25 s, …
TRANSIENT_CODES = {429, 500, 502, 503, 504}

retry_cfg = Retry(
    total=MAX_RETRIES - 1,          # urllib3 counts *retries*
    backoff_factor=BACKOFF_FACTOR,  # exponential delay
    status_forcelist=list(TRANSIENT_CODES),
    allowed_methods=["GET"],
    raise_on_status=False,          # we raise manually after inspecting code
)

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_cfg))

# ╔══════════════════════════════════════════════════════════════════╗
# 3.  Instantiate FastMCP and define tool functions                  ║
# ╚══════════════════════════════════════════════════════════════════╝
mcp = FastMCP("WeatherServer")

@mcp.tool
def get_weather(lat: float, lon: float) -> dict:
    """
    Fetch **current weather** from Open-Meteo and return a concise dict.

    Retry policy
    ------------
    * Up to MAX_RETRIES total attempts.
    * Retries on network errors **or** HTTP 429/5xx.
    * Exponential back-off (1.5 s, 2.25 s, …).

    Parameters
    ----------
    lat, lon : float
        Geographic coordinates in decimal degrees.

    Returns
    -------
    dict
        {
            "temperature": <float °C>,
            "code":        <int WMO weathercode>,
            "conditions":  <friendly description>
        }
    """

@mcp.tool

# ╔══════════════════════════════════════════════════════════════════╗
# 4.  Start the FastMCP HTTP server                                  ║
# ╚══════════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
