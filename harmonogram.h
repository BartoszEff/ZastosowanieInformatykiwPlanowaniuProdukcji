#ifndef HARMONOGRAM_H
#define HARMONOGRAM_H

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

#include <stdio.h>

typedef struct {
    int maszyna;
    int zadanie;
    int start;
    int koniec;
    int przezbrojenie_start;
    int przezbrojenie_koniec;
} Operacja;

EXPORT void inicjalizuj_generator(void);

EXPORT void generuj_dane(int liczba_zadan, int liczba_maszyn,
                         int *czasy_przetwarzania, int *typy_zadan,
                         int *czasy_przezbrojen);

EXPORT int oblicz_makespan(int *kolejnosc_zadan, int liczba_zadan,
                           int liczba_maszyn, int *czasy_przetwarzania,
                           int *typy_zadan, int *czasy_przezbrojen);

EXPORT void symulowane_wyzarzanie(int *kolejnosc_zadan, int liczba_zadan,
                                  int liczba_maszyn, int *czasy_przetwarzania,
                                  int *typy_zadan, int *czasy_przezbrojen,
                                  int *najlepsze_rozwiazanie,
                                  int *wynik_makespan);

EXPORT void brute_force(int *kolejnosc_zadan, int start, int liczba_zadan, int liczba_maszyn,
                        int *czasy_przetwarzania, int *typy_zadan,
                        int *czasy_przezbrojen, int *najlepszy_makespan,
                        int *najlepsze_rozwiazanie);

EXPORT int generuj_dane_harmonogramu(int *kolejnosc_zadan, int liczba_zadan, int liczba_maszyn,
                                     int *czasy_przetwarzania, int *typy_zadan, int *czasy_przezbrojen,
                                     Operacja *operacje);

#endif
