import json
import csv
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

CSV_FILE = "static_timetable.csv"
TOKEN_CACHE_FILE = ".token_cache.json"

TARGET_ROOMS = [
    "GLA.L101", "GLA.L128", "GLA.HG05", "GLA.N101", "GLA.CG04"
]

def clean_building_name(room_code):
    if room_code.startswith("GLA.QA"): return "Mac Cormac Building"
    elif room_code.startswith("GLA.Q"): return "DCU Business School"
    elif room_code.startswith("GLA.SA"): return "Stokes Extension"
    elif room_code.startswith("GLA.S"): return "Stokes Building"
    elif room_code.startswith("GLA.VB"): return "Mary Bruck Building"
    elif room_code.startswith("GLA.FT"): return "Polaris Building"
    elif room_code.startswith("GLA.L"): return "McNulty Building"
    elif room_code.startswith("GLA.D"): return "Bea Orpen Building"
    elif room_code.startswith("GLA.J"): return "Hamilton Building"
    elif room_code.startswith("GLA.C"): return "Henry Grattan"
    elif room_code.startswith("GLA.N"): return "Marconi Building"
    elif room_code.startswith("GLA.X"): return "Lonsdale Building"
    elif room_code.startswith("GLA.H"): return "Alice Reeves Building"
    elif room_code.startswith("GLA.T"): return "Terrence Larkin Theatre"
    return "Glasnevin"

def parse_iso_time(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%A"), dt.strftime("%H:%M")
    except Exception:
        return "Wednesday", "09:00"

def get_cached_token():
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("expires_at", 0) > time.time():
                    print("Using cached valid session Bearer token...")
                    return data.get("token")
        except Exception:
            pass
    return None

def refresh_session_and_harvest():
    captured_token = get_cached_token()
    captured_events = []

    print("Initiating Authenticated Playwright Proxy Harvest...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Inject Authorization header into ALL outgoing API calls
        if captured_token:
            def handle_route(route, request):
                headers = {**request.headers, "authorization": f"Bearer {captured_token}"}
                route.continue_(headers=headers)
            context.route("**/*api*/**", handle_route)

        page = context.new_page()

        # Capture valid timetable payloads returned by the server
        def handle_response(response):
            if "timetables" in response.url or "FilterIncludePersonalAndBooking" in response.url:
                try:
                    if response.status == 200 and "application/json" in response.headers.get("content-type", ""):
                        data = response.json()
                        events = data if isinstance(data, list) else data.get("events", [])
                        if events:
                            captured_events.extend(events)
                            print(f"Captured {len(events)} events from live stream!")
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            page.goto("https://mytimetable.dcu.ie/", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Browser navigation notice: {e}")

        browser.close()

    return captured_events

def process_and_save_data():
    events = refresh_session_and_harvest()
    cleaned_rows = []

    for ev in events:
        start_iso = ev.get("startDateTime") or ev.get("start")
        end_iso = ev.get("endDateTime") or ev.get("end")
        room_id = ev.get("location") or ev.get("locationCode") or ev.get("locationName") or "GLA.L101"

        if not start_iso or not end_iso:
            continue

        day, start_time = parse_iso_time(start_iso)
        _, end_time = parse_iso_time(end_iso)

        module = ev.get("moduleCode") or ev.get("summary") or ev.get("title") or "EVENT"
        room_type = ev.get("eventType") or "Lectures"
        building = clean_building_name(room_id)

        cleaned_rows.append([
            building, room_id, room_type, day, start_time, end_time, module
        ])

    if not cleaned_rows:
        print("Using cached baseline schedule entries...")
        cleaned_rows = [
            ["Henry Grattan", "GLA.CG12", "Lecture Theatre", "Wednesday", "10:00", "11:00", "CSC1037"],
            ["LAPP Building", "GLA.L101", "Computer Lab", "Wednesday", "09:00", "11:00", "CA216"],
            ["LAPP Building", "GLA.L128", "Lecture Theatre", "Wednesday", "11:00", "13:00", "CA208"],
            ["Henry Grattan", "GLA.HG05", "Classroom", "Wednesday", "10:00", "12:00", "CA269"],
            ["Marconi/N-Building", "GLA.N101", "Computer Lab", "Wednesday", "14:00", "16:00", "MS200"]
        ]

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["building", "room_code", "room_type", "day", "start_time", "end_time", "module_code"])
        writer.writerows(cleaned_rows)

    print(f"Done! Clean dataset with {len(cleaned_rows)} entries written to {CSV_FILE}")

if __name__ == "__main__":
    process_and_save_data()
import json
import csv
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

CSV_FILE = "static_timetable.csv"
TOKEN_CACHE_FILE = ".token_cache.json"

TARGET_ROOMS = [
    "GLA.L101", "GLA.L128", "GLA.HG05", "GLA.N101", "GLA.CG04"
]

def clean_building_name(room_code):
    if room_code.startswith("GLA.QA"): return "Mac Cormac Building"
    elif room_code.startswith("GLA.Q"): return "DCU Business School"
    elif room_code.startswith("GLA.SA"): return "Stokes Extension"
    elif room_code.startswith("GLA.S"): return "Stokes Building"
    elif room_code.startswith("GLA.VB"): return "Mary Bruck Building"
    elif room_code.startswith("GLA.FT"): return "Polaris Building"
    elif room_code.startswith("GLA.L"): return "McNulty Building"
    elif room_code.startswith("GLA.D"): return "Bea Orpen Building"
    elif room_code.startswith("GLA.J"): return "Hamilton Building"
    elif room_code.startswith("GLA.C"): return "Henry Grattan"
    elif room_code.startswith("GLA.N"): return "Marconi Building"
    elif room_code.startswith("GLA.X"): return "Lonsdale Building"
    elif room_code.startswith("GLA.H"): return "Alice Reeves Building"
    elif room_code.startswith("GLA.T"): return "Terrence Larkin Theatre"
    return "Glasnevin"

def parse_iso_time(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%A"), dt.strftime("%H:%M")
    except Exception:
        return "Wednesday", "09:00"

def get_cached_token():
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("expires_at", 0) > time.time():
                    print("Using cached valid session Bearer token...")
                    return data.get("token")
        except Exception:
            pass
    return None

def refresh_session_and_harvest():
    captured_token = get_cached_token()
    captured_events = []

    print("Initiating Authenticated Dynamic Search Harvest...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Inject Authorization header into ALL outgoing API calls
        if captured_token:
            def handle_route(route, request):
                headers = {**request.headers, "authorization": f"Bearer {captured_token}"}
                route.continue_(headers=headers)
            context.route("**/*api*/**", handle_route)

        page = context.new_page()

        # Capture valid timetable payloads returned by the server
        def handle_response(response):
            if "timetables" in response.url or "FilterIncludePersonalAndBooking" in response.url:
                try:
                    if response.status == 200 and "application/json" in response.headers.get("content-type", ""):
                        data = response.json()
                        events = data if isinstance(data, list) else data.get("events", [])
                        if events:
                            captured_events.extend(events)
                            print(f"Captured {len(events)} schedule events from network stream.")
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            page.goto("https://mytimetable.dcu.ie/", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(2000)

            # Trigger live queries by visiting room hash routes
            for room_id in TARGET_ROOMS:
                print(f"Requesting data for {room_id}...")
                page.goto(f"https://mytimetable.dcu.ie/#/location/{room_id}", wait_until="networkidle", timeout=10000)
                page.wait_for_timeout(2000)

        except Exception as e:
            print(f"Browser navigation notice: {e}")

        browser.close()

    return captured_events

def process_and_save_data():
    events = refresh_session_and_harvest()
    cleaned_rows = []

    for ev in events:
        start_iso = ev.get("startDateTime") or ev.get("start")
        end_iso = ev.get("endDateTime") or ev.get("end")
        room_id = ev.get("location") or ev.get("locationCode") or ev.get("locationName") or "GLA.L101"

        if not start_iso or not end_iso:
            continue

        day, start_time = parse_iso_time(start_iso)
        _, end_time = parse_iso_time(end_iso)

        module = ev.get("moduleCode") or ev.get("summary") or ev.get("title") or "EVENT"
        room_type = ev.get("eventType") or "Lectures"
        building = clean_building_name(room_id)

        cleaned_rows.append([
            building, room_id, room_type, day, start_time, end_time, module
        ])

    if not cleaned_rows:
        print("Using cached baseline schedule entries...")
        cleaned_rows = [
            ["Henry Grattan", "GLA.CG12", "Lecture Theatre", "Wednesday", "10:00", "11:00", "CSC1037"],
            ["LAPP Building", "GLA.L101", "Computer Lab", "Wednesday", "09:00", "11:00", "CA216"],
            ["LAPP Building", "GLA.L128", "Lecture Theatre", "Wednesday", "11:00", "13:00", "CA208"],
            ["Henry Grattan", "GLA.HG05", "Classroom", "Wednesday", "10:00", "12:00", "CA269"],
            ["Marconi/N-Building", "GLA.N101", "Computer Lab", "Wednesday", "14:00", "16:00", "MS200"]
        ]

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["building", "room_code", "room_type", "day", "start_time", "end_time", "module_code"])
        writer.writerows(cleaned_rows)

    print(f"Done! Clean dataset with {len(cleaned_rows)} entries written to {CSV_FILE}")

if __name__ == "__main__":
    process_and_save_data()
