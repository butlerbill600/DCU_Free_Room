#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 256
#define MAX_ENTRIES 100

typedef struct {
    char building[50];
    char room_code[20];
    char room_type[30];
    char day[15];
    char start_time[10];
    char end_time[10];
    char module_code[30];
} TimetableEntry;

void print_dashboard(TimetableEntry entries[], int count) {
    printf("\n======================================================================\n");
    printf("                    DCU ROOM AVAILABILITY DASHBOARD                   \n");
    printf("======================================================================\n");
    printf("%-20s %-12s %-16s %-10s %-12s\n", "BUILDING", "ROOM", "TYPE", "DAY", "SCHEDULED");
    printf("----------------------------------------------------------------------\n");

    for (int i = 0; i < count; i++) {
        printf("%-20s %-12s %-16s %-10s %s - %s\n",
               entries[i].building,
               entries[i].room_code,
               entries[i].room_type,
               entries[i].day,
               entries[i].start_time,
               entries[i].end_time);
    }
    printf("======================================================================\n\n");
}

int main() {
    FILE *file = fopen("static_timetable.csv", "r");
    if (!file) {
        perror("Error opening static_timetable.csv");
        return 1;
    }

    TimetableEntry entries[MAX_ENTRIES];
    char line[MAX_LINE];
    int count = 0;

    // Skip CSV header row
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return 0;
    }

    while (fgets(line, sizeof(line), file) && count < MAX_ENTRIES) {
        line[strcspn(line, "\r\n")] = 0;

        char *token = strtok(line, ",");
        if (!token) continue;
        strncpy(entries[count].building, token, sizeof(entries[count].building));

        token = strtok(NULL, ",");
        if (!token) continue;
        strncpy(entries[count].room_code, token, sizeof(entries[count].room_code));

        token = strtok(NULL, ",");
        if (!token) continue;
        strncpy(entries[count].room_type, token, sizeof(entries[count].room_type));

        token = strtok(NULL, ",");
        if (!token) continue;
        strncpy(entries[count].day, token, sizeof(entries[count].day));

        token = strtok(NULL, ",");
        if (!token) continue;
        strncpy(entries[count].start_time, token, sizeof(entries[count].start_time));

        token = strtok(NULL, ",");
        if (!token) continue;
        strncpy(entries[count].end_time, token, sizeof(entries[count].end_time));

        token = strtok(NULL, ",");
        if (token) {
            strncpy(entries[count].module_code, token, sizeof(entries[count].module_code));
        }

        count++;
    }

    fclose(file);
    print_dashboard(entries, count);

    return 0;
}
