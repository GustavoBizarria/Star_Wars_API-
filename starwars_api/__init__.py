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
        except urllib.error.URLError as e:
            raise SwapiError(f"connection failure: {e.reason}") from e
        except TimeoutError as e:
            raise SwapiError(f"tempo limite excedido: {e}") from e
 
    def list_resource(self, category: str, page: int = 1, limit: int = 10) -> dict:
        url = f"{self.base_url}/{category}?page={page}&limit={limit}"
        return self._get(url)

    def get_resource(self, category:str, uid: str) -> dict:
        url = f"{self.base_url}/{category}/{uid}"
        return self._get(url)

    def resolve(self, resource_url: str) -> dict:
        return self._get(resource_url)

def format_value(value) -> str:
    if isinstance(value, list):
        return ", ".join(value) if value else "NONE"
    if value in (None, "n/a", "unknown"):
        return "UNKNOWN"
    return str(value)
 
 
def print_header(text: str) -> None:
    print("\n" + "=" * 62)
    print(f"  {text}")
    print("=" * 62)
 
 
def boot_sequence() -> None:
    lines = [
        "INITIALIZING SWAPI TERMINAL...",
        "ESTABLISHING SUBSPATIAL LINK...", 
        "AUTHENTICATING ACCESS CREDENTIALS...", 
        "CONNECTED ESTABLISHED - swapi.tech/api",
    ]
    for line in lines:
        print(f"> {line}")
        time.sleep(0.25)
 
 
def choose_category() -> str:
    print_header("AVAILABLE CATEGORIES")
    for key, (_, label) in CATEGORIES.items():
        print(f"  [{key}] {label}")
    return input("\nChoose a category (or 'q' to quit): ").strip()
 
 
def show_list(client: SwapiClient, category: str, page: int):
    data = client.list_resource(category, page=page)
    results = data.get("results", [])
    total_pages = data.get("total_pages", 1)
    total_records = data.get("total_records", len(results))
 
    print_header(f"{category.upper()} -- pag. {page}/{total_pages} -- {total_records} records")
    for i, item in enumerate(results, start=1 + (page - 1) * 10):
        name = item.get("name") or item.get("uid")
        print(f"  {i:03d}  {name}   (uid={item['uid']})")
    return results, total_pages
 
 
def show_detail(client: SwapiClient, category: str, uid: str) -> None:
    data = client.get_resource(category, uid)
    props = data.get("result", {}).get("properties", {})
 
    title = props.get("name") or props.get("title") or "RECORD"
    print_header(title)
    for key, value in props.items():
        if key in HIDDEN_KEYS:
            continue
        print(f"  {key.upper():<20} {format_value(value)}")
 

    if category == "people" and props.get("homeworld"):
        try:
            hw = client.resolve(props["homeworld"])
            hw_name = hw.get("result", {}).get("properties", {}).get("name")
            if hw_name:
                print(f"\n  -> RESOLVED RELATIONSHIP (homeworld): {hw_name}")
        except SwapiError:
            print("\n  -> it was not possible to solve the home planet.")
 
 
def browse_category(client: SwapiClient, category: str) -> None:
    page = 1
    while True:
        try:
            results, total_pages = show_list(client, category, page)
        except SwapiError as e:
            print(f"\n[ERRO] {e}")
            return
 
        print("\n[n] next page  [p] previous page  [number] open record  [r] return")
        action = input("> ").strip().lower()
 
        if action == "r":
            return
        if action == "n" and page < total_pages:
            page += 1
            continue
        if action == "p" and page > 1:
            page -= 1
            continue
        if action.isdigit():
            index = int(action) - 1 - (page - 1) * 10
            if 0 <= index < len(results):
                uid = results[index]["uid"]
                try:
                    show_detail(client, category, uid)
                except SwapiError as e:
                    print(f"\n[ERROR] {e}")
                input("\nPress ENTER to continue...")
            else:
                print("Number outside the range of this page.")
            continue
        print("Command not recognized.")

def main() -> None:
    boot_sequence()
    client = SwapiClient()

    while True:
        choice = choose_category()
        if choice.lower() == "q":
            print("\nClosing broadcast. May the Force be with you.")
            break
        if choice not in CATEGORIES:
            print("Invalid option.")
            continue
        category, _ = CATEGORIES[choice]
        browse_category(client, category)


if __name__ == "__main__":
    main()