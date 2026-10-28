# DCU Free Room Finder 

A lightweight CLI tool and pipeline for real-time room availability across Dublin City University (Glasnevin Campus) classrooms and O'Reilly Library Group Study Rooms (GSRs).

It combines static academic timetable schedules with live scraped LibCal data, mapping daily availability into a high-precision 48-slot bitmap engine in C to display discrete, non-contiguous free time windows.

---

## Features

- **Hybrid Data Pipeline:** Merges static campus timetables (`static_timetable.csv`) with live library bookings (`live_libcal.csv`).
- **High-Precision Bitmap Engine:** Uses a 48-slot array (30-minute granularity) per room to accurately compute open windows.
- **Discrete Gap Parsing:** Renders multiple non-contiguous free blocks side-by-side (e.g., `14:00–15:00 17:00–18:00`) instead of truncating at the first continuous block.
- **Automated Scraping:** Uses Python & Playwright to target live LibCal DOM grid entries while filtering out system buffer/padding slots.
- **Local Testing & Date Shifts:** Supports live scraping for today and simulated date shifts for tomorrow.

---

## Project Structure

```text
├── main.c                 # Core C engine (CSV parsing, bitmap array, terminal UI rendering)
├── fetch_libcal.py        # Python/Playwright scraper for live LibCal availability
├── static_timetable.csv   # Static classroom schedule data
├── live_libcal.csv        # Output of fetch_libcal.py (overwritten per scrape)
└── Makefile               # Automated build & pipeline execution commands
