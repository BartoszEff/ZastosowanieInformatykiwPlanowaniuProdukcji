#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MULTIPLIER 16807
#define MODULUS 2147483647

int generator(int *seed) {
    *seed = (int)(((long long)MULTIPLIER * (*seed)) % MODULUS);
    return *seed;
}

void generate_processing_times(int num_jobs, int num_machines,int seed, int processing_times[num_jobs][num_machines]) {
    int current_seed = seed;
    for (int i = 0; i < num_jobs; i++) {
        for (int j = 0; j < num_machines; j++) {
            processing_times[i][j] = generator(&current_seed) % 100 + 1;
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
    int seed = (int)time(NULL);
    int num_jobs = 5;
    int num_machines = 3;
    int processing_times[num_jobs][num_machines];
    generate_processing_times(num_jobs, num_machines, seed, processing_times);
    print_processing_times(num_jobs, num_machines, processing_times);
    return 0;
}