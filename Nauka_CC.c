#include <stdio.h>
#include <stdlib.h>
#include <time.h>




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
int calculate_makespan()
{
    return 0;
}
//void simulated_annealing(int jobs[], int num_jobs, int num_machines, int processing_times[num_machines][num_jobs], int job_types[num_jobs], int setup_times[num_machines]) {


//}
int akceptacja()
{
    return 0;
}
int liczenie_makespan()
{
    return 0;
}
void sasiedztwo()
{

}

int main() {
    srand(time(0));
    int num_jobs = 5;
    int num_machines = 3;
    int processing_times[num_jobs][num_machines];
    int setup_times[num_machines];
    int job_types[num_jobs];
   /*  int jobs[num_jobs];
    for (int i = 0; i < num_jobs; i++) {
        jobs[i] = i;
    } */
    generate_processing_times(num_jobs, num_machines, processing_times, job_types, setup_times);
    print_processing_times(num_jobs, num_machines, processing_times, job_types, setup_times);
    //simulated_annealing(jobs, num_jobs, num_machines, processing_times, job_types, setup_times);
    return 0;
}