CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = dcu-free-room
SRC = main.c

PY_TIMETABLE = fetch_timetable.py
PY_LIBCAL = fetch_libcal.py

.PHONY: all fetch fetch_libcal build run clean help

all: build

fetch:
	@echo "Fetching DCU Campus Timetable data..."
	python3 $(PY_TIMETABLE)

fetch_libcal:
	@echo "Fetching Live O'Reilly Library Space Availability..."
	python3 $(PY_LIBCAL)

build: $(SRC)
	@echo "Compiling C Engine..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

run: fetch_libcal build
	./$(TARGET)

clean:
	rm -f $(TARGET) static_timetable.csv live_libcal.csv

help:
	@echo "Usage"
	@echo "  make fetch        - Run full Python campus scraper"
	@echo "  make fetch_libcal - Fetch live O'Reilly Library room bookings"
	@echo "  make build        - Compile C executable"
	@echo "  make run          - Fetch live library data, compile, and run CLI"
	@echo "  make clean        - Clean binaries and temporary files"
