import ctypes
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ctypes import Structure, c_int

from guietta import Gui, _, Quit

# Ładowanie DLL i definicja funkcji C jak poprzednio
dll_path = 'C:/Users/beffe/OneDrive/Desktop/ZastosowanieInformatykiwPlanowaniuProdukcji/harmonogram.dll'
try:
    lib = ctypes.CDLL(dll_path)
except OSError as e:
    print(f"Błąd podczas ładowania biblioteki DLL: {e}")
    sys.exit(1)

class Operacja(Structure):
    _fields_ = [
        ('maszyna', c_int),
        ('zadanie', c_int),
        ('start', c_int),
        ('koniec', c_int),
        ('przezbrojenie_start', c_int),
        ('przezbrojenie_koniec', c_int)
    ]

lib.inicjalizuj_generator.argtypes = []
lib.inicjalizuj_generator.restype = None
lib.inicjalizuj_generator()

lib.generuj_dane.argtypes = [c_int, c_int, ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(c_int)]
lib.generuj_dane.restype = None

lib.symulowane_wyzarzanie.argtypes = [
    ctypes.POINTER(c_int), c_int, c_int, ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(c_int),
    ctypes.POINTER(c_int), ctypes.POINTER(c_int)
]
lib.symulowane_wyzarzanie.restype = None

lib.brute_force.argtypes = [
    ctypes.POINTER(c_int), c_int, c_int, c_int,
    ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(c_int),
    ctypes.POINTER(c_int), ctypes.POINTER(c_int)
]
lib.brute_force.restype = None

lib.generuj_dane_harmonogramu.argtypes = [
    ctypes.POINTER(c_int), c_int, c_int, ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(Operacja)
]
lib.generuj_dane_harmonogramu.restype = c_int

# Zmienne globalne
liczba_zadan = 0
liczba_maszyn = 0
czasy_przetwarzania = None
typy_zadan = None
czasy_przezbrojen = None
kolejnosc_zadan = None
najlepsze_rozwiazanie_symulowane = None
najlepsze_rozwiazanie_brute = None

def generuj_dane_fun(gui):
    global liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen, kolejnosc_zadan
    global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

    liczba_zadan = int(gui.zadania)
    liczba_maszyn = int(gui.maszyny)

    czasy_przetwarzania = (c_int * (liczba_zadan * liczba_maszyn))()
    typy_zadan = (c_int * liczba_zadan)()
    czasy_przezbrojen = (c_int * liczba_maszyn)()
    kolejnosc_zadan = (c_int * liczba_zadan)(*range(liczba_zadan))
    najlepsze_rozwiazanie_symulowane = (c_int * liczba_zadan)()
    najlepsze_rozwiazanie_brute = (c_int * liczba_zadan)()

    lib.generuj_dane(liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen)
    print(f"Wygenerowano dane dla {liczba_zadan} zadań i {liczba_maszyn} maszyn")

def wyzarzanie_fun(gui):
    global najlepsze_rozwiazanie_symulowane
    wynik_makespan_sa = c_int()
    lib.symulowane_wyzarzanie(
        kolejnosc_zadan,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        najlepsze_rozwiazanie_symulowane,
        ctypes.byref(wynik_makespan_sa)
    )
    print(f"Symulowane wyżarzanie wykonane, makespan: {wynik_makespan_sa.value}")

def brute_fun(gui):
    global najlepsze_rozwiazanie_brute
    wynik_makespan_bf = c_int()
    lib.brute_force(
        kolejnosc_zadan,
        0,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        ctypes.byref(wynik_makespan_bf),
        najlepsze_rozwiazanie_brute
    )
    print(f"Brute force wykonane, makespan: {wynik_makespan_bf.value}")

def rysuj_gantta(harmonogram, tytul):
    max_operacji = liczba_zadan * liczba_maszyn
    operacje = (Operacja * max_operacji)()
    liczba_operacji = lib.generuj_dane_harmonogramu(
        harmonogram,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        operacje
    )
    lista_operacji = [operacje[i] for i in range(liczba_operacji)]

    fig, ax = plt.subplots(figsize=(8,4))
    if liczba_operacji == 0:
        return fig

    num_zadan = max(op.zadanie for op in lista_operacji) + 1
    cmap = plt.get_cmap('tab20', num_zadan)
    kolory = [cmap(i) for i in range(num_zadan)]

    for op in lista_operacji:
        y = liczba_maszyn - op.maszyna - 1
        czas_przezbrojenia = op.przezbrojenie_koniec - op.przezbrojenie_start
        if czas_przezbrojenia > 0:
            ax.broken_barh([(op.przezbrojenie_start, czas_przezbrojenia)], (y - 0.4, 0.8), facecolors='gray', alpha=0.5)
        czas_operacji = op.koniec - op.start
        ax.broken_barh([(op.start, czas_operacji)], (y - 0.4, 0.8), facecolors=kolory[op.zadanie])

    ax.set_ylim(-1, liczba_maszyn)
    ax.set_xlim(0, max(op.koniec for op in lista_operacji) + 10)
    ax.set_xlabel('Czas')
    ax.set_ylabel('Maszyna')
    ax.set_yticks(range(liczba_maszyn))
    ax.set_yticklabels([f'M{m+1}' for m in range(liczba_maszyn)][::-1])
    ax.grid(True)
    plt.title(tytul)
    plt.tight_layout()
    return fig

def wykres_sa(gui):
    fig = rysuj_gantta(najlepsze_rozwiazanie_symulowane, "Wykres SA")
    fig.show()

def wykres_brute(gui):
    fig = rysuj_gantta(najlepsze_rozwiazanie_brute, "Wykres Brute-force")
    fig.show()

# Definicja GUI w guietta
# guietta pozwala definiować GUI jako siatkę:
# 'zadania' i 'maszyny' to nazwy zmiennych pola tekstowego, 'Generuj dane' i inne
# to przyciski. '_' to puste miejsce. Quit to przycisk zamknięcia.


gui = Gui(
  ['Liczba zadań:', '__zadania__', 'Liczba maszyn:', '__maszyny__'],
  [ 'Generuj dane', 'Wyżarzanie', 'Brute force', 'Wykres SA', 'Wykres Brute', Quit ]
)

# Mapowanie zdarzeń przycisków na funkcje
gui.events(
  [  _, generuj_dane_fun, wyzarzanie_fun, brute_fun, wykres_sa, wykres_brute, _]
)

# Uruchom GUI
gui.run()
