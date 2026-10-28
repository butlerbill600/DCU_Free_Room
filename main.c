#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ROOMS 256
#define MAX_LINE 256
#define START_SLOT 28  // 14:00 (slot 28)
#define END_SLOT 40    // 20:00 (slot 40)

typedef struct {
    char building[64];
    char room_code[32];
    char room_type[32];
    int is_booked[48]; // 48 half-hour slots per day (0 = Free, 1 = Booked)
} Room;

Room rooms[MAX_ROOMS];
int room_count = 0;

int get_or_create_room(const char *building, const char *room_code, const char *room_type) {
    for (int i = 0; i < room_count; i++) {
        if (strcmp(rooms[i].room_code, room_code) == 0) {
            return i;
        }
    }

    if (room_count >= MAX_ROOMS) return -1;

    int idx = room_count++;
    strncpy(rooms[idx].building, building, sizeof(rooms[idx].building) - 1);
    strncpy(rooms[idx].room_code, room_code, sizeof(rooms[idx].room_code) - 1);
    strncpy(rooms[idx].room_type, room_type, sizeof(rooms[idx].room_type) - 1);
    
    for (int s = 0; s < 48; s++) {
        rooms[idx].is_booked[s] = 0;
    }

    return idx;
}

void load_csv(const char *filepath) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) return;

    char line[MAX_LINE];
    if (!fgets(line, sizeof(line), fp)) {
        fclose(fp);
        return;
    }

    while (fgets(line, sizeof(line), fp)) {
        char building[64], room_code[32], room_type[32], day[16], start_t[16], end_t[16], module[32];

        int fields = sscanf(line, " %63[^,],%31[^,],%31[^,],%15[^,],%15[^,],%15[^,],%31[^\n]",
                            building, room_code, room_type, day, start_t, end_t, module);

        if (fields < 6) continue;

        int room_idx = get_or_create_room(building, room_code, room_type);
        if (room_idx < 0) continue;

        if (strcmp(module, "INIT") == 0 || strcmp(start_t, "00:00") == 0) {
            continue;
        }

        int s_hr = 0, s_min = 0, e_hr = 0, e_min = 0;
        sscanf(start_t, "%d:%d", &s_hr, &s_min);
        sscanf(end_t, "%d:%d", &e_hr, &e_min);

        int start_slot = (s_hr * 2) + (s_min >= 30 ? 1 : 0);
        int end_slot = (e_hr * 2) + (e_min >= 30 ? 1 : 0);

        for (int s = start_slot; s < end_slot && s < 48; s++) {
            rooms[room_idx].is_booked[s] = 1;
        }
    }

    fclose(fp);
}

int main(void) {
    load_csv("static_timetable.csv");
    load_csv("live_libcal.csv");

    printf("=================================================================================\n");
    printf("        DCU GLASNEVIN & O'REILLY LIBRARY — UNOCCUPIED ROOMS (14:00 ONWARDS)\n");
    printf("=================================================================================\n");
    printf("%-20s %-12s %-18s %s\n", "BUILDING", "ROOM", "TYPE", "AVAILABLE 1-HOUR SLOTS TODAY");
    printf("---------------------------------------------------------------------------------\n");

    for (int i = 0; i < room_count; i++) {
        printf("%-20s %-12s %-18s ", rooms[i].building, rooms[i].room_code, rooms[i].room_type);

        int printed_any = 0;

        // Step through hour by hour (every 2 half-hour slots)
        for (int s = START_SLOT; s < END_SLOT; s += 2) {
            // Check if full hour (both 30-min sub-slots) is unbooked
            if (!rooms[i].is_booked[s] && !rooms[i].is_booked[s + 1]) {
                int start_hr = s / 2;
                int end_hr = start_hr + 1;
                printf("%02d:00–%02d:00 ", start_hr, end_hr);
                printed_any = 1;
            }
        }

        if (!printed_any) {
            printf("NO FREE SLOTS");
        }

        printf("\n");
    }

    printf("=================================================================================\n");

    return 0;
}
