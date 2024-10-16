#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void generate_processing_times(int num_jobs, int num_machines, int processing_times[num_jobs][num_machines]) {
    for (int i = 0; i < num_jobs; i++) {
        for (int j = 0; j < num_machines; j++) {
            processing_times[i][j] = rand() % 100 + 1;
        }
    }
}

void print_processing_times(int num_jobs, int num_machines, int processing_times[num_jobs][num_machines]) {
    for (int i = 0; i < num_jobs; i++) {
        for (int j = 0; j < num_machines; j++) {
            printf("%d\t", processing_times[i][j]);
        }
        printf("\n");
    }
}
int main() {
    srand((int)time(NULL));
    int num_jobs = 5;
    int num_machines = 3;
    int processing_times[num_jobs][num_machines];
    generate_processing_times(num_jobs, num_machines, processing_times);
    print_processing_times(num_jobs, num_machines, processing_times);
    return 0;
}
