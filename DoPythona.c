#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>
#include <string.h>
#include <math.h>

// Funkcja generująca dane
void generuj_dane(int liczba_zadan, int liczba_maszyn, int *czasy_przetwarzania, int *typy_zadan, int *czasy_przezbrojen) {
    for (int i = 0; i < liczba_zadan; i++) {
        for (int j = 0; j < liczba_maszyn; j++) {
            czasy_przetwarzania[i * liczba_maszyn + j] = rand() % 100 + 1; 
        }
        typy_zadan[i] = rand() % 2;
    }
    for (int j = 0; j < liczba_maszyn; j++) {
        czasy_przezbrojen[j] = rand() % 50 + 1;
    }
}

// Funkcja obliczająca makespan
int oblicz_makespan(int *kolejnosc_zadan, int liczba_zadan, int liczba_maszyn, int *czasy_przetwarzania, int *typy_zadan, int *czasy_przezbrojen) {
    int *czasy_zakonczenia_maszyn = (int *)malloc(sizeof(int) * liczba_maszyn);
    memset(czasy_zakonczenia_maszyn, 0, sizeof(int) * liczba_maszyn);
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
            int koniec_poprzedniej_maszyny = (m > 0) ? czasy_zakonczenia_maszyn[m - 1] : 0;

            int start_zadania = fmax(start_przezbrojenia + czas_przezbrojenia, koniec_poprzedniej_maszyny);
            int koniec_zadania = start_zadania + czasy_przetwarzania[zadanie * liczba_maszyn + m];
            czasy_zakonczenia_maszyn[m] = koniec_zadania;
        }
        makespan = fmax(makespan, czasy_zakonczenia_maszyn[liczba_maszyn - 1]);
    }
    free(czasy_zakonczenia_maszyn);
    return makespan;
}

// Funkcja generująca sąsiednie rozwiązanie
void generuj_sasiedztwo(int *kolejnosc_zadan, int liczba_zadan, int *sasiednie_rozwiazanie) {
    memcpy(sasiednie_rozwiazanie, kolejnosc_zadan, sizeof(int) * liczba_zadan);
    int i = rand() % liczba_zadan;
    int j = rand() % liczba_zadan;
    while (i == j) {
        j = rand() % liczba_zadan;
    }
    int temp = sasiednie_rozwiazanie[i];
    sasiednie_rozwiazanie[i] = sasiednie_rozwiazanie[j];
    sasiednie_rozwiazanie[j] = temp;
}

// Funkcja symulowanego wyżarzania
void symulowane_wyzarzanie(int *kolejnosc_zadan, int liczba_zadan, int liczba_maszyn, int *czasy_przetwarzania, int *typy_zadan, int *czasy_przezbrojen, int *najlepsze_rozwiazanie) {
    double temperatura = 1000.0;
    double wspolczynnik_chlodzenia = 0.95;
    double minimalna_temperatura = 0.05;
    int maks_iteracji = 1000;
    int brak_poprawy = 0;
    int maks_brak_poprawy = 900;
    int aktualny_makespan = oblicz_makespan(kolejnosc_zadan, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    int najlepszy_makespan = aktualny_makespan;
    memcpy(najlepsze_rozwiazanie, kolejnosc_zadan, sizeof(int) * liczba_zadan);

    while (temperatura > minimalna_temperatura && brak_poprawy < maks_brak_poprawy) {
        for (int i = 0; i < maks_iteracji; i++) {
            int *sasiednie_rozwiazanie = (int *)malloc(sizeof(int) * liczba_zadan);
            generuj_sasiedztwo(kolejnosc_zadan, liczba_zadan, sasiednie_rozwiazanie);
            int makespan_sasiada = oblicz_makespan(sasiednie_rozwiazanie, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
            int delta = makespan_sasiada - aktualny_makespan;
            double prawdopodobienstwo = exp(-((double)delta) / temperatura);
            double losowa = (double)rand() / RAND_MAX;
            if (delta < 0 || prawdopodobienstwo > losowa) {
                memcpy(kolejnosc_zadan, sasiednie_rozwiazanie, sizeof(int) * liczba_zadan);
                aktualny_makespan = makespan_sasiada;

                if (aktualny_makespan < najlepszy_makespan) {
                    memcpy(najlepsze_rozwiazanie, kolejnosc_zadan, sizeof(int) * liczba_zadan);
                    najlepszy_makespan = aktualny_makespan;
                    brak_poprawy = 0;
                }
            }
            free(sasiednie_rozwiazanie);
        }
        temperatura *= wspolczynnik_chlodzenia;
        brak_poprawy++;
    }

    printf("Najlepszy makespan z symulowanego wyżarzania: %d\n", najlepszy_makespan);
}

// Funkcja NEH
void neh(int liczba_zadan, int liczba_maszyn, int *czasy_przetwarzania, int *typy_zadan, int *czasy_przezbrojen, int *neh_schedule) {
    int *suma_czasow_przetwarzania = (int *)malloc(sizeof(int) * liczba_zadan);
    for (int i = 0; i < liczba_zadan; i++) {
        suma_czasow_przetwarzania[i] = 0;
        for (int j = 0; j < liczba_maszyn; j++) {
            suma_czasow_przetwarzania[i] += czasy_przetwarzania[i * liczba_maszyn + j];
        }
    }
    int *posortowane_zadania = (int *)malloc(sizeof(int) * liczba_zadan);
    for (int i = 0; i < liczba_zadan; i++) {
        posortowane_zadania[i] = i;
    }
    // Sortowanie zadań malejąco według sumy czasów przetwarzania
    for (int i = 0; i < liczba_zadan - 1; i++) {
        for (int j = 0; j < liczba_zadan - i - 1; j++) {
            if (suma_czasow_przetwarzania[posortowane_zadania[j]] < suma_czasow_przetwarzania[posortowane_zadania[j + 1]]) {
                int temp = posortowane_zadania[j];
                posortowane_zadania[j] = posortowane_zadania[j + 1];
                posortowane_zadania[j + 1] = temp;
            }
        }
    }
    int *aktualny_harmonogram = (int *)malloc(sizeof(int) * liczba_zadan);
    aktualny_harmonogram[0] = posortowane_zadania[0];
    int aktualna_dlugosc = 1;
    for (int i = 1; i < liczba_zadan; i++) {
        int zadanie_do_dodania = posortowane_zadania[i];
        int najlepszy_makespan = INT_MAX;
        int najlepsza_pozycja = 0;
        int *tymczasowy_harmonogram = (int *)malloc(sizeof(int) * (aktualna_dlugosc + 1));
        for (int pos = 0; pos <= aktualna_dlugosc; pos++) {
            for (int k = 0; k < pos; k++) {
                tymczasowy_harmonogram[k] = aktualny_harmonogram[k];
            }
            tymczasowy_harmonogram[pos] = zadanie_do_dodania;
            for (int k = pos; k < aktualna_dlugosc; k++) {
                tymczasowy_harmonogram[k + 1] = aktualny_harmonogram[k];
            }
            int tymczasowy_makespan = oblicz_makespan(tymczasowy_harmonogram, aktualna_dlugosc + 1, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
            if (tymczasowy_makespan < najlepszy_makespan) {
                najlepszy_makespan = tymczasowy_makespan;
                najlepsza_pozycja = pos;
            }
        }
        for (int k = aktualna_dlugosc; k > najlepsza_pozycja; k--) {
            aktualny_harmonogram[k] = aktualny_harmonogram[k - 1];
        }
        aktualny_harmonogram[najlepsza_pozycja] = zadanie_do_dodania;
        aktualna_dlugosc++;
        free(tymczasowy_harmonogram);
    }
    for (int i = 0; i < liczba_zadan; i++) {
        neh_schedule[i] = aktualny_harmonogram[i];
    }
    int neh_makespan = oblicz_makespan(neh_schedule, liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen);
    printf("\nNajlepszy makespan z algorytmu NEH: %d\n", neh_makespan);
    free(suma_czasow_przetwarzania);
    free(posortowane_zadania);
    free(aktualny_harmonogram);
}
