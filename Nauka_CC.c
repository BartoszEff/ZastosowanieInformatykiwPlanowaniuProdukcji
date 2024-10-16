#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MULTIPLIER 16807
#define MODULUS 2147483647

unsigned int taillard_random(unsigned int *seed) {
    *seed = (unsigned int)(((unsigned long long)MULTIPLIER * (*seed)) % MODULUS);
    return *seed;
}

void generate_processing_times(int num_jobs, int num_machines, unsigned int seed, int processing_times[num_jobs][num_machines], float job_types[num_jobs], int setup_times[num_machines]) {
    unsigned int current_seed = seed;
    for (int i = 0; i < num_jobs; i++) {
        for (int j = 0; j < num_machines; j++) {
            processing_times[i][j] = taillard_random(&current_seed) % 100 + 1;
        }
        job_types[i] = (float)taillard_random(&current_seed) / MODULUS;
    }
    for (int j = 0; j < num_machines; j++) {
        setup_times[j] = taillard_random(&current_seed) % 50 + 1;
    }
}

void print_processing_times(int num_jobs, int num_machines, int processing_times[num_jobs][num_machines], float job_types[num_jobs], int setup_times[num_machines]) {
    printf("Czasy przezbrojenia dla każdej maszyny:\n");
    for (int j = 0; j < num_machines; j++) {
        printf("Maszyna %d: %d\n", j + 1, setup_times[j]);
    }
    printf("\n");
    for (int i = 0; i < num_jobs; i++) {
        printf("Typ zadania %d: %.2f\n", i + 1, job_types[i]);
        for (int j = 0; j < num_machines; j++) {
            printf("%d\t", processing_times[i][j]);
        }
        printf("\n");
    }
}
int main() {
    unsigned int seed = (unsigned int)time(NULL);
    int num_jobs = 5;
    int num_machines = 3;
    int processing_times[num_jobs][num_machines];
    int setup_times[num_machines];
    float job_types[num_jobs];
    generate_processing_times(num_jobs, num_machines, seed, processing_times, job_types, setup_times);
    print_processing_times(num_jobs, num_machines, processing_times, job_types, setup_times);
    return 0;
}