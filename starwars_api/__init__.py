import json 
import time 
import urllib.request
import urllib.error

BASE_URL = "https://www.swapi.tech/api"

CATEGORIES = {
    "1": ("people", "Peaple"),
    "2": ("planets", "Planets"),
    "3": ("starships", "Starships"),
    "4": ("vehicles", "Vehicles"),
    "5": ("species", "Species"),
    "6": ("films", "Films"),
}

# Internal metadata
HIDDEN_KEYS = {"created", "edited", "url", "homeworld"}

class SwapiError(Exception):
    """API communication error (network, HTTP, timeout)."""

class SwapiClient:

    """
    Data access layer. Isolates the rest of the program from the details of
    transport (urllib, headers, timeout, HTTP error handling).
    Swapping from swapi.tech to another SWAPI implementation means
    just mess around here.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    def _get(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"User-Agent": ""})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise SwapiError(f"HTTP {e.code} when acessing {url}") from e
        