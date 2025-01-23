import ctypes
import sys


try:
    lib = ctypes.CDLL('C:/Users/beffe/OneDrive/Desktop/ZastosowanieInformatykiwPlanowaniuProdukcji/harmonogram.dll')
except OSError as e:
    print(f"Błąd podczas ładowania biblioteki DLL: {e}")
    sys.exit(1)

lib.inicjalizuj_generator.argtypes = []
lib.inicjalizuj_generator.restype = None

lib.generuj_dane.argtypes = [
    ctypes.c_int,  
    ctypes.c_int,  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int)   
]
lib.generuj_dane.restype = None

lib.symulowane_wyzarzanie.argtypes = [
    ctypes.POINTER(ctypes.c_int),  
    ctypes.c_int,                  
    ctypes.c_int,                  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int)  
]
lib.symulowane_wyzarzanie.restype = None

lib.neh.argtypes = [
    ctypes.c_int,                 
    ctypes.c_int,                  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int), 
    ctypes.POINTER(ctypes.c_int)   
]
lib.neh.restype = None

lib.brute_force.argtypes = [
    ctypes.POINTER(ctypes.c_int),  
    ctypes.c_int,                  
    ctypes.c_int,                  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int), 
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int), 
    ctypes.POINTER(ctypes.c_int)   
]
lib.brute_force.restype = None
lib.inicjalizuj_generator()

while True:
    try:
        liczba_zadan = int(input("Podaj liczbę zadań: "))
        liczba_maszyn = int(input("Podaj liczbę maszyn: "))
        if liczba_zadan <= 0 or liczba_maszyn <= 0:
            print("Liczba zadań i maszyn musi być większa od zera.")
            continue
        break
    except ValueError:
        print("Proszę podać poprawną liczbę całkowitą.")

# Sprawdź ograniczenia dla brute force
if liczba_zadan > 5 or liczba_maszyn > 8:
    can_use_brute_force = False
    print("Ze względu na ograniczenia, algorytm brute-force nie zostanie uruchomiony (maksymalnie 5 zadań i 8 maszyn).")
else:
    can_use_brute_force = True

# Alokacja tablic
czasy_przetwarzania = (ctypes.c_int * (liczba_zadan * liczba_maszyn))()
typy_zadan = (ctypes.c_int * liczba_zadan)()
czasy_przezbrojen = (ctypes.c_int * liczba_maszyn)()
kolejnosc_zadan = (ctypes.c_int * liczba_zadan)(*list(range(liczba_zadan)))
najlepsze_rozwiazanie_symulowane = (ctypes.c_int * liczba_zadan)()
najlepsze_rozwiazanie_neh = (ctypes.c_int * liczba_zadan)()
najlepsze_rozwiazanie_brute = (ctypes.c_int * liczba_zadan)()
najlepszy_makespan_brute = ctypes.c_int()

lib.generuj_dane(
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen
)

lib.symulowane_wyzarzanie(
    kolejnosc_zadan,
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen,
    najlepsze_rozwiazanie_symulowane
)

lib.neh(
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen,
    najlepsze_rozwiazanie_neh
)

lib.wyswietl_harmonogram_maszyn.argtypes = [
    ctypes.POINTER(ctypes.c_int),  
    ctypes.c_int,                  
    ctypes.c_int,                  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int)   
]
lib.wyswietl_harmonogram_maszyn.restype = None

if can_use_brute_force:
    lib.brute_force(
        kolejnosc_zadan,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        ctypes.byref(najlepszy_makespan_brute),
        najlepsze_rozwiazanie_brute
    )

print("\nHarmonogram maszyn z symulowanego wyżarzania:")
lib.wyswietl_harmonogram_maszyn(
    najlepsze_rozwiazanie_symulowane,
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen
)
print("\nHarmonogram maszyn z algorytmu NEH:")
lib.wyswietl_harmonogram_maszyn(
    najlepsze_rozwiazanie_neh,
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen
)
if can_use_brute_force:
    print("\nHarmonogram maszyn z brute-force:")
    lib.wyswietl_harmonogram_maszyn(
        najlepsze_rozwiazanie_brute,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen
    )
