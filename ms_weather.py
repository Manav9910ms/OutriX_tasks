import os
import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime, timedelta

# --- Configuration ---
API_KEY = os.getenv("OPENWEATHER_API_KEY", "647b6ed4337d18247e2c242de430a8fe")

CURRENT_URL  = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"   # 5-day / 3-hour
ONECALL_URL  = "https://api.openweathermap.org/data/3.0/onecall"     # Daily min/max (may require subscription)

SESSION = requests.Session()
TIMEOUT = 10  # seconds


def get_weather():
    city = city_var.get().strip()
    if not city:
        set_status("Please enter a city name.", "#b71c1c")
        clear_cards()
        return

    set_status("Loading...", "#0d47a1")
    root.after(50, lambda: fetch_and_render(city))


def fetch_and_render(city: str):
    try:
        # 1) Current conditions (for display + coords + timezone)
        cur_params = {"q": city, "appid": API_KEY, "units": "metric"}
        r = SESSION.get(CURRENT_URL, params=cur_params, timeout=TIMEOUT)
        handle_http_errors(r)
        current = r.json()

        weather   = current["weather"][0]["description"].title()
        temp      = f"{round(current['main']['temp'], 1)} °C"
        humidity  = f"{current['main']['humidity']} %"
        name      = current["name"]
        country   = current["sys"]["country"]
        lat       = current["coord"]["lat"]
        lon       = current["coord"]["lon"]
        tz_offset = current.get("timezone", 0)  # seconds offset from UTC

        # 2) Daily min/max
        tmin, tmax = get_today_minmax(lat, lon, city, tz_offset)

        # 3) Render UI
        set_status(f"{name}, {country}", "#0d47a1")
        update_card("Desc", weather)
        update_card("Temp", temp)
        update_card("Min", f"{round(tmin, 1)} °C")
        update_card("Max", f"{round(tmax, 1)} °C")
        update_card("Humidity", humidity)

    except requests.HTTPError as e:
        msg = friendly_http_error(e.response)
        set_status(msg, "#b71c1c")
        clear_cards()
    except requests.RequestException:
        set_status("Network error.", "#b71c1c")
        clear_cards()
    except KeyError as e:
        set_status(f"Unexpected data format: missing {e}", "#b71c1c")
        clear_cards()
    except Exception as e:
        set_status(f"Error: {e}", "#b71c1c")
        clear_cards()


def get_today_minmax(lat: float, lon: float, city: str, tz_offset_sec: int):
    """
    Try One Call (daily min/max). If unavailable (401/404/429/etc.), fall back to
    computing today's min/max from the 5-day/3-hour forecast.
    """
    # Attempt One Call 3.0
    try:
        oc_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "exclude": "minutely,hourly,alerts",
        }
        r = SESSION.get(ONECALL_URL, params=oc_params, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            daily = data.get("daily", [])
            if daily:
                today = daily[0]["temp"]
                return float(today["min"]), float(today["max"])
        else:
            # Non-200 means plan/quota/access issues or other errors; fall through to forecast
            pass
    except requests.RequestException:
        pass

    # Fall back: 5-day/3-hour forecast
    fc_params = {"q": city, "appid": API_KEY, "units": "metric"}
    r = SESSION.get(FORECAST_URL, params=fc_params, timeout=TIMEOUT)
    handle_http_errors(r)
    forecast = r.json()

    items = forecast.get("list", [])
    if not items:
        raise ValueError("Forecast data unavailable.")

    # Determine today's local date for the location
    now_local = datetime.utcnow() + timedelta(seconds=tz_offset_sec)
    today_local_date = now_local.date()

    # Select all forecast slices that occur on the same local date
    todays_slices = []
    for it in items:
        t_local = datetime.utcfromtimestamp(it["dt"]) + timedelta(seconds=tz_offset_sec)
        if t_local.date() == today_local_date:
            todays_slices.append(it)

    # If it's late-night and no slices remain for "today", use next 24 hours
    if not todays_slices:
        end_window = now_local + timedelta(hours=24)
        for it in items:
            t_local = datetime.utcfromtimestamp(it["dt"]) + timedelta(seconds=tz_offset_sec)
            if now_local <= t_local <= end_window:
                todays_slices.append(it)

    if not todays_slices:
        raise ValueError("No forecast slices found for today/next 24h.")

    # Compute min/max using temp_min/temp_max; fall back to temp if needed
    mins = []
    maxs = []
    for it in todays_slices:
        main = it.get("main", {})
        if "temp_min" in main and "temp_max" in main:
            mins.append(main["temp_min"])
            maxs.append(main["temp_max"])
        elif "temp" in main:
            mins.append(main["temp"])
            maxs.append(main["temp"])

    if not mins or not maxs:
        raise ValueError("Incomplete forecast data for min/max.")

    return min(mins), max(maxs)


def handle_http_errors(resp: requests.Response):
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # Attach payload text for clearer diagnosis
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        e.response.detail = detail
        raise


def friendly_http_error(resp: requests.Response) -> str:
    code = resp.status_code
    # Try to surface server message if available
    detail = getattr(resp, "detail", None)
    if isinstance(detail, dict) and "message" in detail:
        server_msg = detail["message"]
    elif isinstance(detail, str):
        server_msg = detail.strip()
    else:
        server_msg = None

    if code == 401:
        return "Unauthorized: Check your API key or plan for this endpoint."
    if code == 404:
        return "City not found."
    if code == 429:
        return "Rate limit exceeded. Try again later."
    if code == 400:
        return f"Bad request: {server_msg or 'Please verify inputs.'}"
    return f"HTTP {code}: {server_msg or 'Request failed.'}"


def update_card(title, text):
    frame, label = cards[title]
    label.config(text=text)
    frame.grid()


def clear_cards():
    for frame, _ in cards.values():
        frame.grid_remove()


def set_status(text, color):
    status_label.config(text=text, foreground=color)


# --- UI ---
root = tk.Tk()
root.title("Manav Weather Forecast")
root.geometry("420x400")
root.resizable(False, False)
root.configure(bg="#e3f2fd")

style = ttk.Style(root)
style.theme_use("clam")

style.configure(
    "Header.TLabel",
    background="#2196f3",
    foreground="white",
    font=("Segoe UI", 16, "bold"),
    padding=10,
)
style.configure("TFrame", background="#e3f2fd")
style.configure("TEntry", font=("Segoe UI", 12), padding=5)
style.configure(
    "TButton",
    font=("Segoe UI", 8, "bold"),
    padding=6,
)
style.map("TButton", background=[("active", "#1565c0")])
style.configure(
    "Card.TLabelframe",
    background="white",
    borderwidth=1,
    relief="solid",
    padding=8,
)
style.configure(
    "Card.TLabelframe.Label",
    background="white",
    font=("Segoe UI", 10, "bold"),
    foreground="#1e88e5",
)

header = ttk.Label(root, text="Manav Weather Forecast", style="Header.TLabel")
header.pack(fill=tk.X)

search_frame = ttk.Frame(root, padding=10)
search_frame.pack(fill=tk.X)

city_var = tk.StringVar()
lbl_city = ttk.Label(search_frame, text="Enter City:")
lbl_city.grid(row=0, column=0, padx=(0, 5))
city_entry = ttk.Entry(search_frame, textvariable=city_var, width=20)
city_entry.grid(row=0, column=1)
btn_search = ttk.Button(search_frame, text="Search", command=get_weather)
btn_search.grid(row=0, column=2, padx=6)
city_entry.bind("<Return>", lambda e: get_weather())

status_label = ttk.Label(root, text="Type a city and click Search")
status_label.pack(pady=(0, 10))

cards_frame = ttk.Frame(root, padding=10)
cards_frame.pack(fill=tk.BOTH, expand=True)

fields = ["Desc", "Temp", "Min", "Max", "Humidity"]
cards = {}
for idx, name in enumerate(fields):
    lf = ttk.Labelframe(cards_frame, text=name, style="Card.TLabelframe")
    lbl = ttk.Label(lf, text="", font=("Segoe UI", 12))
    lbl.pack(expand=True)
    row, col = divmod(idx, 2)
    lf.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
    lf.grid_remove()
    cards[name] = (lf, lbl)

for i in range(3):
    cards_frame.rowconfigure(i, weight=1)
for j in range(2):
    cards_frame.columnconfigure(j, weight=1)

root.mainloop()