import csv
import re
from playwright.sync_api import sync_playwright

CSV_FILE = "live_libcal.csv"

def parse_libcal_availability():
    print("Fetching live LibCal booked slots...")
    url = "https://dcu-ie.libcal.com/reserve/spaces/oreilly"
    csv_rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector(".s-lc-eq-period-booked", timeout=15000)

            # Extract booked elements
            booked_slots = page.evaluate("""
                () => {
                    const results = [];
                    const elements = document.querySelectorAll('div.s-lc-eq-period-booked');
                    
                    elements.forEach(el => {
                        const start = el.getAttribute('data-period-start') || '';
                        const end = el.getAttribute('data-period-end') || '';
                        const title = el.getAttribute('data-original-title') || el.getAttribute('title') || '';
                        
                        if (start && end) {
                            results.push({ start, end, title });
                        }
                    });
                    
                    return results;
                }
            """)

            for slot in booked_slots:
                title = slot['title']
                start_str = slot['start']
                end_str = slot['end']

                room_match = re.search(r'GSR\s*(\d+)', title)
                if not room_match:
                    continue
                room_code = f"LIB.GSR{room_match.group(1)}"

                # Extract time strings (e.g. "14:00", "17:30")
                start_time = start_str.split()[1][:5] if ' ' in start_str else start_str[:5]
                end_time = end_str.split()[1][:5] if ' ' in end_str else end_str[:5]

                csv_rows.append([
                    "O'Reilly Library", room_code, "Group Study Room", "Today", start_time, end_time, "LIB_RESERVED"
                ])

        except Exception as e:
            print(f"Extraction error: {e}")

        browser.close()

    # Seed all library rooms so they register in C engine
    known_gsrs = ["LIB.GSR1", "LIB.GSR6", "LIB.GSR7", "LIB.GSR9", "LIB.GSR10", "LIB.GSR13", "LIB.GSR14", "LIB.GSR15", "LIB.GSR16"]
    for g in known_gsrs:
        csv_rows.append(["O'Reilly Library", g, "Group Study Room", "Today", "00:00", "00:00", "INIT"])

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["building", "room_code", "room_type", "day", "start_time", "end_time", "module_code"])
        writer.writerows(csv_rows)

    print(f"Saved {len(csv_rows)} booked slot entries to {CSV_FILE}.")

if __name__ == "__main__":
    parse_libcal_availability()
