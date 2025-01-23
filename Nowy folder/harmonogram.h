// harmonogram.h

#ifndef HARMONOGRAM_H
#define HARMONOGRAM_H

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

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
                                  int *najlepsze_rozwiazanie);

EXPORT void neh(int liczba_zadan, int liczba_maszyn,
                int *czasy_przetwarzania, int *typy_zadan,
                int *czasy_przezbrojen, int *neh_schedule);

EXPORT void brute_force(int *kolejnosc_zadan, int liczba_zadan, int liczba_maszyn,
                        int *czasy_przetwarzania, int *typy_zadan,
                        int *czasy_przezbrojen, int *najlepszy_makespan,
                        int *najlepsze_rozwiazanie);

EXPORT void wyswietl_harmonogram_maszyn(int *kolejnosc_zadan, int liczba_zadan, int liczba_maszyn,
                                        int *czasy_przetwarzania, int *typy_zadan, int *czasy_przezbrojen);




#ifdef __cplusplus
}
#endif

#endif // HARMONOGRAM_H

