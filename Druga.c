#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>
#include <string.h>
#include <math.h>

void generuj_dane(int liczba_zadan, int liczba_maszyn, int czasy_przetwarzania[liczba_zadan][liczba_maszyn],int typy_zadan[liczba_zadan], int czasy_przezbrojen[liczba_maszyn]) {
    for (int i = 0; i < liczba_zadan; i++) {
        for (int j = 0; j < liczba_maszyn; j++) {
            czasy_przetwarzania[i][j] = rand() % 100 + 1; 
        }
        typy_zadan[i] = rand() % 2;
    }
    for (int j = 0; j < liczba_maszyn; j++) {
        czasy_przezbrojen[j] = rand() % 50 + 1;
    }
}
/* void wyswietl_dane(int liczba_zadan, int liczba_maszyn,
                   int czasy_przetwarzania[liczba_zadan][liczba_maszyn],
                   int typy_zadan[liczba_zadan],
                   int czasy_przezbrojen[liczba_maszyn]) {
    printf("Czasy przezbrojenia maszyn:\n");
    for (int j = 0; j < liczba_maszyn; j++) {
        printf("Maszyna %d: %d\n", j + 1, czasy_przezbrojen[j]);
    }
    printf("\nCzasy przetwarzania zadań:\n");
    for (int i = 0; i < liczba_zadan; i++) {
        printf("Zadanie %d (Typ %d): ", i + 1, typy_zadan[i]);
        for (int j = 0; j < liczba_maszyn; j++) {
            printf("%d ", czasy_przetwarzania[i][j]);
        }
        printf("\n");
    }
} */
int oblicz_makespan(int kolejnosc_zadan[], int liczba_zadan, int liczba_maszyn, int czasy_przetwarzania[liczba_zadan][liczba_maszyn], int typy_zadan[liczba_zadan], int czasy_przezbrojen[liczba_maszyn]) {
    int czasy_zakonczenia_maszyn[liczba_maszyn];
    memset(czasy_zakonczenia_maszyn, 0, liczba_maszyn * sizeof(int));
    int makespan = 0;

    for (int i = 0; i < liczba_zadan; i++) {
        int zadanie = kolejnosc_zadan[i];
        for (int m = 0; m < liczba_maszyn; m++) {
            int czas_przezbrojenia;
            if (i > 0 && typy_zadan[kolejnosc_zadan[i - 1]] != typy_zadan[zadanie]) {
                czas_przezbrojenia = 10 * czasy_przezbrojen[m];
            } else {
                czas_przezbrojenia = czasy_przezbrojen[m];
            }

            int start_przezbrojenia = czasy_zakonczenia_maszyn[m];
            int koniec_poprzedniej_maszyny;
            if (m > 0) {
                koniec_poprzedniej_maszyny = czasy_zakonczenia_maszyn[m - 1];
            } else {
                koniec_poprzedniej_maszyny = 0;
            }

            int start_zadania = fmax(start_przezbrojenia + czas_przezbrojenia, koniec_poprzedniej_maszyny);
            int koniec_zadania = start_zadania + czasy_przetwarzania[zadanie][m];
            czasy_zakonczenia_maszyn[m] = koniec_zadania;
        }
        makespan = fmax(makespan, czasy_zakonczenia_maszyn[liczba_maszyn - 1]);
    }
    return makespan;
}
void generuj_sasiedztwo(int kolejnosc_zadan[], int liczba_zadan, int sasiednie_rozwiazanie[]) {
    memcpy(sasiednie_rozwiazanie, kolejnosc_zadan, liczba_zadan * sizeof(int));
    int i = rand() % liczba_zadan;
    int j = rand() % liczba_zadan;
    while (i == j) {
        j = rand() % liczba_zadan;
    }
    int temp = sasiednie_rozwiazanie[i];
    sasiednie_rozwiazanie[i] = sasiednie_rozwiazanie[j];
    sasiednie_rozwiazanie[j] = temp;
}
void symulowane_wyzarzanie(int kolejnosc_zadan[], int liczba_zadan, int liczba_maszyn, int czasy_przetwarzania[liczba_zadan][liczba_maszyn], int typy_zadan[liczba_zadan], int czasy_przezbrojen[liczba_maszyn],int najlepsze_rozwiazanie[]) {
    double temperatura = 1000.0;
    double wspolczynnik_chlodzenia = 0.95;
    double minimalna_temperatura = 0.05;
    int maks_iteracji = 1000;
    int brak_poprawy = 0;
    int maks_brak_poprawy = 500;
    int aktualny_makespan = oblicz_makespan(kolejnosc_zadan, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    int najlepszy_makespan = aktualny_makespan;
    memcpy(najlepsze_rozwiazanie, kolejnosc_zadan, liczba_zadan * sizeof(int));
    while (temperatura > minimalna_temperatura && brak_poprawy < maks_brak_poprawy) {
        for (int i = 0; i < maks_iteracji; i++) {
            int sasiednie_rozwiazanie[liczba_zadan];
            generuj_sasiedztwo(kolejnosc_zadan, liczba_zadan, sasiednie_rozwiazanie);
            int makespan_sasiada = oblicz_makespan(sasiednie_rozwiazanie, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
            int delta = makespan_sasiada - aktualny_makespan;
            double prawdopodobienstwo = exp(-delta / temperatura);
            double losowa = (double)rand() / RAND_MAX;
            if (delta < 0 || prawdopodobienstwo > losowa) {
                memcpy(kolejnosc_zadan, sasiednie_rozwiazanie, liczba_zadan * sizeof(int));
                aktualny_makespan = makespan_sasiada;

                if (aktualny_makespan < najlepszy_makespan) {
                    memcpy(najlepsze_rozwiazanie, kolejnosc_zadan, liczba_zadan * sizeof(int));
                    najlepszy_makespan = aktualny_makespan;
                    brak_poprawy = 0;
                }
            }
        }
        temperatura *= wspolczynnik_chlodzenia;
        brak_poprawy++;
    }

    printf("Najlepszy makespan z symulowanego wyzarzania: %d\n", najlepszy_makespan);
}
void brute_force(int kolejnosc_zadan[], int start, int liczba_zadan, int liczba_maszyn, int czasy_przetwarzania[liczba_zadan][liczba_maszyn], int typy_zadan[liczba_zadan], int czasy_przezbrojen[liczba_maszyn], int *najlepszy_makespan, int najlepsze_rozwiazanie[]) {
    if (start == liczba_zadan) {
        int aktualny_makespan = oblicz_makespan(kolejnosc_zadan, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
        if (aktualny_makespan < *najlepszy_makespan) {
            *najlepszy_makespan = aktualny_makespan;
            memcpy(najlepsze_rozwiazanie, kolejnosc_zadan, liczba_zadan * sizeof(int));
        }
        return;
    }
    for (int i = start; i < liczba_zadan; i++) {
        int temp = kolejnosc_zadan[start];
        kolejnosc_zadan[start] = kolejnosc_zadan[i];
        kolejnosc_zadan[i] = temp;
        brute_force(kolejnosc_zadan, start + 1, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen, najlepszy_makespan, najlepsze_rozwiazanie);
        temp = kolejnosc_zadan[start];
        kolejnosc_zadan[start] = kolejnosc_zadan[i];
        kolejnosc_zadan[i] = temp;
    }
}

void wyswietl_harmonogram_zadan(int kolejnosc_zadan[], int liczba_zadan, int liczba_maszyn,int czasy_przetwarzania[liczba_zadan][liczba_maszyn],int typy_zadan[liczba_zadan], int czasy_przezbrojen[liczba_maszyn]) {
    int czasy_zakonczenia_maszyn[liczba_maszyn];
    memset(czasy_zakonczenia_maszyn, 0, liczba_maszyn * sizeof(int));
    for (int i = 0; i < liczba_zadan; i++) {
        printf("Zadanie %d:\n", kolejnosc_zadan[i] + 1);

        for (int m = 0; m < liczba_maszyn; m++) {
            int czas_przezbrojenia;
            if (i > 0 && typy_zadan[kolejnosc_zadan[i - 1]] != typy_zadan[kolejnosc_zadan[i]]) {
                czas_przezbrojenia = 10 * czasy_przezbrojen[m];
            } else {
                czas_przezbrojenia = czasy_przezbrojen[m];
            }

            int start_przezbrojenia = czasy_zakonczenia_maszyn[m];

            int koniec_poprzedniej_maszyny;
            if (m > 0) {
                koniec_poprzedniej_maszyny = czasy_zakonczenia_maszyn[m - 1];
            } else {
                koniec_poprzedniej_maszyny = 0;
            }

            int start_zadania = fmax(start_przezbrojenia + czas_przezbrojenia, koniec_poprzedniej_maszyny);
            /*if (start_przezbrojenia + czas_przezbrojenia > koniec_poprzedniej_maszyny) {
            start_zadania = start_przezbrojenia + czas_przezbrojenia;
            } else {
             start_zadania = koniec_poprzedniej_maszyny;
            }*/
            int koniec_zadania = start_zadania + czasy_przetwarzania[kolejnosc_zadan[i]][m];
            czasy_zakonczenia_maszyn[m] = koniec_zadania;
            printf("  [M%d: Przezbrojenie %d-%d] [Zadanie %d: %d-%d]\n", m + 1, start_przezbrojenia, start_przezbrojenia + czas_przezbrojenia, kolejnosc_zadan[i] + 1, start_zadania, koniec_zadania);
        }
        printf("\n");
    }
}
void wyswietl_harmonogram_maszyn(int kolejnosc_zadan[], int liczba_zadan, int liczba_maszyn, int czasy_przetwarzania[liczba_zadan][liczba_maszyn], int typy_zadan[liczba_zadan], int czasy_przezbrojen[liczba_maszyn]) {
    int czasy_zakonczenia_maszyn[liczba_maszyn];
    memset(czasy_zakonczenia_maszyn, 0, liczba_maszyn * sizeof(int));
    /* for (int i = 0; i < liczba_maszyn; i++) {
    czasy_zakonczenia_maszyn[i] = 0;
    } */
    int czasy_zakonczenia_zadan[liczba_zadan][liczba_maszyn];
    memset(czasy_zakonczenia_zadan, 0, liczba_zadan * liczba_maszyn * sizeof(int));
    /* for (int i = 0; i < liczba_zadan; i++) {
    czasy_zakonczenia_zadan[i] = 0;
    } */
    for (int m = 0; m < liczba_maszyn; m++) {
        printf("Maszyna %d: ", m + 1);
        for (int i = 0; i < liczba_zadan; i++) {
            int zadanie = kolejnosc_zadan[i];

            int czas_przezbrojenia;
            if (i > 0 && typy_zadan[kolejnosc_zadan[i - 1]] != typy_zadan[zadanie]) {
                czas_przezbrojenia = 10 * czasy_przezbrojen[m]; 
            } else {
                czas_przezbrojenia = czasy_przezbrojen[m];
            }
            int start_przezbrojenia = czasy_zakonczenia_maszyn[m];
            int koniec_przezbrojenia = start_przezbrojenia + czas_przezbrojenia;
            int koniec_poprzedniej_maszyny;
            if (m > 0) {
                koniec_poprzedniej_maszyny = czasy_zakonczenia_zadan[zadanie][m - 1];
            } else {
                koniec_poprzedniej_maszyny = 0;
            }

            int start_zadania = fmax(koniec_przezbrojenia, koniec_poprzedniej_maszyny);
            int koniec_zadania = start_zadania + czasy_przetwarzania[zadanie][m];
            czasy_zakonczenia_maszyn[m] = koniec_zadania;
            czasy_zakonczenia_zadan[zadanie][m] = koniec_zadania;
            printf("[Zad%d: P: %d-%d (Zadanie: %d-%d)]",  zadanie + 1 ,start_przezbrojenia, koniec_przezbrojenia, start_zadania, koniec_zadania);
        }
        printf("\n");
    }
}
int main() {
    srand(time(0));
    int liczba_zadan = 10;
    int liczba_maszyn = 5;
    int czasy_przetwarzania[liczba_zadan][liczba_maszyn];
    int czasy_przezbrojen[liczba_maszyn];
    int typy_zadan[liczba_zadan];
    int kolejnosc_zadan[liczba_zadan];
    int najlepsze_rozwiazanie_symulowane[liczba_zadan];
    int najlepsze_rozwiazanie_brute[liczba_zadan];
    for (int i = 0; i < liczba_zadan; i++) {
        kolejnosc_zadan[i] = i;
    }
    generuj_dane(liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    //wyswietl_dane(liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    symulowane_wyzarzanie(kolejnosc_zadan, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen, najlepsze_rozwiazanie_symulowane);
    wyswietl_harmonogram_zadan(najlepsze_rozwiazanie_symulowane, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    wyswietl_harmonogram_maszyn(najlepsze_rozwiazanie_symulowane, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    int najlepszy_makespan_brute = INT_MAX;
    brute_force(kolejnosc_zadan, 0, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen, &najlepszy_makespan_brute, najlepsze_rozwiazanie_brute);
    printf("\nNajlepszy makespan z brute-force: %d\n", najlepszy_makespan_brute);
    wyswietl_harmonogram_zadan(najlepsze_rozwiazanie_brute, liczba_zadan, liczba_maszyn,czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    wyswietl_harmonogram_maszyn(najlepsze_rozwiazanie_brute, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    return 0;
}
