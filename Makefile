CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = dcu-free-room
SRC = main.c

PY_TIMETABLE = fetch_timetable.py

.PHONY: all fetch build run clean help

all: build

fetch:
	@echo "Fetching DCU Timetable data..."
	python3 $(PY_TIMETABLE)

build: $(SRC)
	@echo "Compiling C Engine..."
	$(CC) $(CFLAGS) -o (Target) $(SRC)

run: build
	./$(TARGET)

clean:
	rm -f $(TARGET) static_timetable.csv live_libcal.json

help:
	@echo "Usage"
	@echo "  make fetch  - Run Python scraper to generate CSV timetable"
	@echo "  make build  - Compile the C executable"
	@echo "  make run    - Compile and run the CLI room finder"
	@echo "  make clean  - Remove compiled binaries and generated data files"

