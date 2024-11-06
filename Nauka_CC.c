#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <math.h>



void generate_processing_times(int num_jobs, int num_machines, int processing_times[num_jobs][num_machines], int job_types[num_jobs], int setup_times[num_machines]) {
    for (int i = 0; i < num_jobs; i++) {
        for (int j = 0; j < num_machines; j++) {
            processing_times[i][j] = rand() % 100 + 1;
        }
        job_types[i] = (int)rand() % 2;
    }
    for (int j = 0; j < num_machines; j++) {
        setup_times[j] = rand() % 50 + 1;
    }
}

void print_processing_times(int num_jobs, int num_machines, int processing_times[num_jobs][num_machines], int job_types[num_jobs], int setup_times[num_machines]) {
    for (int j = 0; j < num_machines; j++) {
        printf("Maszyna %d: %d\n", j + 1, setup_times[j]);
    }
    printf("\n");
    for (int i = 0; i < num_jobs; i++) {
        printf("Typ zadania %d: %d\n", i + 1, job_types[i]);
        for (int j = 0; j < num_machines; j++) {
            printf("%d\t", processing_times[i][j]);
        }
        printf("\n");
    }
}


void sasiedztwo(int jobs[], int num_jobs, int neighbor[]){
     memcpy(neighbor, jobs, num_jobs * sizeof(int));
    int i = rand() % num_jobs;
    int j = rand() % num_jobs;
    while (i == j) {
        j = rand() % num_jobs;
    } 
    int temp = neighbor[i];
    neighbor[i] = neighbor[j];
   neighbor[j] = temp;

    //int i = rand() % (num_jobs - 1);
    //int temp = neighbor[i];
    //neighbor[i] = neighbor[i + 1];
    //neighbor[i + 1] = temp; 


}


 int liczenie_makespan(int jobs[], int num_jobs, int num_machines, int processing_times[num_jobs][num_machines], int job_types[], int setup_times[]) {
    (void)jobs;
    (void)processing_times;
    (void)job_types;
    (void)setup_times;
    return 0;
}

void simulated_annealing(int jobs[], int num_jobs, int num_machines, int processing_times[num_machines][num_jobs], int job_types[num_jobs], int setup_times[num_machines]) {
    double T = 1000.0; 
    double alpha = 0.95; 
    double Tmin = 0.01; 
    int max_iterations = 1000;
    int current_makespan = liczenie_makespan(jobs, num_jobs, num_machines, processing_times, job_types, setup_times);
    int best_makespan = current_makespan;
    int best_jobs[num_jobs];
    memcpy(best_jobs, jobs, num_jobs * sizeof(int));
    while (T > Tmin) {
        for (int i = 0; i < max_iterations; i++) {
            int neighbor[num_jobs];
            sasiedztwo(jobs, num_jobs, neighbor);
            int neighbor_makespan = liczenie_makespan(neighbor, num_jobs, num_machines, processing_times, job_types, setup_times);

            if (neighbor_makespan < current_makespan || ((double)rand() / RAND_MAX) < exp((current_makespan - neighbor_makespan) / T)) {
                memcpy(jobs, neighbor, num_jobs * sizeof(int));
                current_makespan = neighbor_makespan;

                if (current_makespan < best_makespan) {
                    memcpy(best_jobs, jobs, num_jobs * sizeof(int));
                    best_makespan = current_makespan;
                }
            }
        }
        T *= alpha;
    }

    printf("Najlepszy makespan: %d\n", best_makespan);

}

 double akceptacja(int current_makespan, int new_makespan, double T)
{
    if (new_makespan < current_makespan) {
        return 1.0;
    }
    return exp((current_makespan - new_makespan) / T);
} 


int main() {
    srand(time(0));
    int num_jobs = 5;
    int num_machines = 3;
    int processing_times[num_jobs][num_machines];
    int setup_times[num_machines];
    int job_types[num_jobs];
     int jobs[num_jobs];
    for (int i = 0; i < num_jobs; i++) {
        jobs[i] = i;
    } 
    generate_processing_times(num_jobs, num_machines, processing_times, job_types, setup_times);
    print_processing_times(num_jobs, num_machines, processing_times, job_types, setup_times);
    simulated_annealing(jobs, num_jobs, num_machines, processing_times, job_types, setup_times);
    return 0;
}